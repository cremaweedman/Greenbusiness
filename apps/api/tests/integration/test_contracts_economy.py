from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import (
    ContractCompletion,
    CurrencyLedgerEntry,
    InventoryContainer,
    InventoryItem,
    User,
)
from app.db.session import SessionLocal
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as value:
        yield value


async def _cleanup(email: str) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user is not None:
            await session.delete(user)
            await session.commit()


async def _register(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "A-strong-password-789",
            "display_name": "Contractor",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


async def _grant_inventory(email: str, item_key: str, quantity: int) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        inventory = await session.scalar(
            select(InventoryContainer).where(InventoryContainer.user_id == user.id)
        )
        assert inventory is not None
        item = InventoryItem(
            inventory_container_id=inventory.id,
            item_key=item_key,
            quantity=quantity,
        )
        session.add(item)
        await session.commit()


@pytest.mark.asyncio
async def test_contract_completion_consumes_inventory_and_writes_cash_ledger(client: AsyncClient):
    email = f"p3-contract-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        initial_player = await client.get("/v1/player", headers=auth)
        assert initial_player.status_code == 200
        initial_state = initial_player.json()
        assert initial_state["cash_balance"] == 0
        quick_contract = initial_state["contracts"][0]
        assert quick_contract["key"] == "quick-counter-sample"
        assert quick_contract["can_complete"] is False
        assert quick_contract["completed"] is False
        assert initial_state["contract_board"]["reroll_cost"] == 25
        assert initial_state["contract_board"]["rerolls_remaining"] == 3
        assert [contract["key"] for contract in initial_state["contract_board"]["contracts"]] == [
            "quick-counter-sample",
            "standard-lounge-restock",
        ]

        listed = await client.get("/v1/contracts", headers=auth)
        assert listed.status_code == 200
        assert listed.json()[0]["key"] == quick_contract["key"]

        board = await client.get("/v1/contracts/board", headers=auth)
        assert board.status_code == 200
        assert board.json()["contracts"][0]["key"] == quick_contract["key"]

        poor_reroll = await client.post("/v1/contracts/reroll", headers=auth)
        assert poor_reroll.status_code == 409
        assert poor_reroll.json()["error"]["code"] == "CONTRACT_REROLL_CASH_INSUFFICIENT"

        missing = await client.post(f"/v1/contracts/{quick_contract['key']}/complete", headers=auth)
        assert missing.status_code == 409
        assert missing.json()["error"]["code"] == "CONTRACT_REQUIREMENT_MISSING"

        await _grant_inventory(email, "starter_crop.aurora-drift", 2)

        available = await client.get("/v1/contracts", headers=auth)
        assert available.json()[0]["can_complete"] is True

        completed = await client.post(f"/v1/contracts/{quick_contract['key']}/complete", headers=auth)
        assert completed.status_code == 200
        completion = completed.json()
        assert completion["cash_delta"] == 45
        assert completion["cash_balance"] == 45
        assert completion["reputation_delta"] == 1
        assert completion["reputation"] == 1
        assert completion["contract"]["completed"] is True
        assert completion["contract"]["reputation_reward"] == 1
        assert completion["inventory"][0]["quantity"] == 0

        replay = await client.post(f"/v1/contracts/{quick_contract['key']}/complete", headers=auth)
        assert replay.status_code == 409
        assert replay.json()["error"]["code"] == "CONTRACT_ALREADY_COMPLETED"

        final_player = await client.get("/v1/player", headers=auth)
        final_state = final_player.json()
        assert final_state["cash_balance"] == 45
        assert final_state["reputation"] == 1
        assert final_state["progression"]["reputation"] == 1
        assert final_state["economy_summary"] == {
            "currency": "cash",
            "balance": 45,
            "minted": 45,
            "burned": 0,
            "entry_count": 1,
            "config_versions": ["p3-contracts-v1"],
        }
        assert final_state["cash_ledger"][0]["amount"] == 45
        assert final_state["cash_ledger"][0]["balance_after"] == 45
        assert final_state["contracts"][0]["completed"] is True
        assert final_state["contracts"][0]["can_complete"] is False

        cash_ledger = await client.get("/v1/economy/cash-ledger", headers=auth)
        assert cash_ledger.status_code == 200
        assert cash_ledger.json()[0]["source_id"] == quick_contract["key"]

        economy_summary = await client.get("/v1/economy/summary", headers=auth)
        assert economy_summary.status_code == 200
        assert economy_summary.json()["minted"] == 45
        assert economy_summary.json()["burned"] == 0

        reroll = await client.post("/v1/contracts/reroll", headers=auth)
        assert reroll.status_code == 200
        reroll_body = reroll.json()
        assert reroll_body["cash_delta"] == -25
        assert reroll_body["cash_balance"] == 20
        assert reroll_body["board"]["rerolls_used"] == 1
        assert reroll_body["board"]["rerolls_remaining"] == 2
        assert [contract["key"] for contract in reroll_body["board"]["contracts"]] == [
            "premium-night-market",
            "quick-counter-sample",
        ]
        assert reroll_body["economy_summary"]["burned"] == 25

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            ledger_entries = (
                await session.scalars(
                    select(CurrencyLedgerEntry)
                    .where(CurrencyLedgerEntry.user_id == user.id)
                    .order_by(CurrencyLedgerEntry.created_at, CurrencyLedgerEntry.id)
                )
            ).all()
            completions = (
                await session.scalars(
                    select(ContractCompletion).where(ContractCompletion.user_id == user.id)
                )
            ).all()

        assert len(ledger_entries) == 2
        assert ledger_entries[0].balance_before == 0
        assert ledger_entries[0].balance_after == 45
        assert ledger_entries[0].config_version == "p3-contracts-v1"
        assert ledger_entries[1].amount == -25
        assert ledger_entries[1].balance_after == 20
        assert len(completions) == 1
        assert completions[0].contract_key == "quick-counter-sample"
        assert completions[0].reputation_reward == 1
    finally:
        await _cleanup(email)
