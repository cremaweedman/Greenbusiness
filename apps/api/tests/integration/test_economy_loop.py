from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.db.models import (
    CropProduction,
    EconomyLedger,
    PlayerUpgrade,
    User,
    Wallet,
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
            "password": "A-strong-password-999",
            "display_name": "Economy",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


async def _force_ready(slot_id: str) -> None:
    async with SessionLocal() as session:
        crop = await session.scalar(
            select(CropProduction)
            .where(CropProduction.slot_id == uuid.UUID(slot_id))
            .where(CropProduction.harvested_at.is_(None))
        )
        assert crop is not None
        crop.ready_at = datetime.now(UTC) - timedelta(seconds=1)
        await session.commit()


@pytest.mark.asyncio
async def test_economic_loop_is_idempotent_and_upgrade_changes_yield(client: AsyncClient):
    email = f"p3-{uuid.uuid4()}@example.com"

    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        initial = await client.get("/v1/player", headers=auth)
        assert initial.status_code == 200
        state = initial.json()
        assert state["cash"] == 500
        assert state["contract_offers"][0]["key"] == "neighborhood-sampler"
        assert state["contract_offers"][0]["required_quantity"] == 3
        assert state["contract_offers"][0]["reward_cash"] == 150
        assert state["upgrade_offers"][0]["key"] == "starter-yield-boost"
        assert state["upgrade_offers"][0]["cost_cash"] == 600
        assert state["owned_upgrade_keys"] == []

        too_early = await client.post(
            "/v1/economy/upgrades/starter-yield-boost/purchase",
            headers={**auth, "Idempotency-Key": "upgrade-too-early"},
        )
        assert too_early.status_code == 409
        assert too_early.json()["error"]["code"] == "ECONOMY_CASH_INSUFFICIENT"

        slot_id = state["slots"][0]["id"]
        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200

        await _force_ready(slot_id)
        first_harvest = await client.post(
            f"/v1/production/slots/{slot_id}/harvest",
            headers=auth,
        )
        assert first_harvest.status_code == 200
        assert first_harvest.json()["yield_quantity"] == 3
        assert first_harvest.json()["harvested_item"]["quantity"] == 3

        accepted = await client.post(
            "/v1/economy/contracts/neighborhood-sampler/accept",
            headers=auth,
        )
        assert accepted.status_code == 200
        contract_id = accepted.json()["id"]
        assert accepted.json()["status"] == "active"

        completed = await client.post(
            f"/v1/economy/contracts/{contract_id}/complete",
            headers={**auth, "Idempotency-Key": "contract-complete-1"},
        )
        assert completed.status_code == 200
        completed_state = completed.json()
        assert completed_state["cash"] == 650
        assert completed_state["active_contract"]["status"] == "completed"
        assert completed_state["inventory"][0]["quantity"] == 0
        assert completed_state["reputation"] == 5

        replayed = await client.post(
            f"/v1/economy/contracts/{contract_id}/complete",
            headers={**auth, "Idempotency-Key": "contract-complete-1"},
        )
        assert replayed.status_code == 200
        assert replayed.json()["cash"] == 650

        purchased = await client.post(
            "/v1/economy/upgrades/starter-yield-boost/purchase",
            headers={**auth, "Idempotency-Key": "upgrade-purchase-1"},
        )
        assert purchased.status_code == 200
        purchased_state = purchased.json()
        assert purchased_state["cash"] == 50
        assert purchased_state["owned_upgrade_keys"] == ["starter-yield-boost"]

        purchase_replay = await client.post(
            "/v1/economy/upgrades/starter-yield-boost/purchase",
            headers={**auth, "Idempotency-Key": "upgrade-purchase-1"},
        )
        assert purchase_replay.status_code == 200
        assert purchase_replay.json()["cash"] == 50

        second_plant = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert second_plant.status_code == 200
        await _force_ready(slot_id)

        upgraded_harvest = await client.post(
            f"/v1/production/slots/{slot_id}/harvest",
            headers=auth,
        )
        assert upgraded_harvest.status_code == 200
        assert upgraded_harvest.json()["yield_quantity"] == 4

        final = await client.get("/v1/player", headers=auth)
        assert final.status_code == 200
        final_state = final.json()
        assert final_state["cash"] == 50
        assert final_state["owned_upgrade_keys"] == ["starter-yield-boost"]
        assert final_state["upgrade_offers"][0]["key"] == "efficient-racks-2"
        assert final_state["upgrade_offers"][0]["locked"] is True

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None

            wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user.id))
            assert wallet is not None
            assert wallet.cash == 50

            ledger_entries = (
                await session.scalars(
                    select(EconomyLedger)
                    .where(EconomyLedger.user_id == user.id)
                    .order_by(EconomyLedger.created_at, EconomyLedger.id)
                )
            ).all()
            assert [entry.amount for entry in ledger_entries] == [500, 150, -600]
            assert all(entry.balance_after >= 0 for entry in ledger_entries)
            assert await session.scalar(
                select(func.count())
                .select_from(PlayerUpgrade)
                .where(PlayerUpgrade.user_id == user.id)
            ) == 1
    finally:
        await _cleanup(email)
