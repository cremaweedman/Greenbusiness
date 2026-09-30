from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import CropProduction, CurrencyLedgerEntry, User
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
            "display_name": "Upgrader",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


async def _grant_cash(email: str, amount: int) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        session.add(
            CurrencyLedgerEntry(
                user_id=user.id,
                currency="cash",
                source="test_grant",
                source_id=str(uuid.uuid4()),
                amount=amount,
                balance_before=0,
                balance_after=amount,
                config_version="test",
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_upgrade_spends_cash_and_changes_future_harvest_yield(client: AsyncClient):
    email = f"p3-upgrade-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        initial = await client.get("/v1/player", headers=auth)
        assert initial.status_code == 200
        initial_state = initial.json()
        upgrade = initial_state["upgrades"][0]
        assert upgrade["key"] == "starter-bench-calibration"
        assert upgrade["can_purchase"] is False

        insufficient = await client.post(f"/v1/upgrades/{upgrade['key']}/purchase", headers=auth)
        assert insufficient.status_code == 409
        assert insufficient.json()["error"]["code"] == "UPGRADE_CASH_INSUFFICIENT"

        await _grant_cash(email, 100)

        available = await client.get("/v1/upgrades", headers=auth)
        assert available.status_code == 200
        assert available.json()[0]["can_purchase"] is True

        purchased = await client.post(f"/v1/upgrades/{upgrade['key']}/purchase", headers=auth)
        assert purchased.status_code == 200
        purchase_body = purchased.json()
        assert purchase_body["cash_delta"] == -100
        assert purchase_body["cash_balance"] == 0
        assert purchase_body["upgrade"]["level"] == 1
        assert purchase_body["economy_summary"]["minted"] == 100
        assert purchase_body["economy_summary"]["burned"] == 100

        duplicate = await client.post(f"/v1/upgrades/{upgrade['key']}/purchase", headers=auth)
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "UPGRADE_MAX_LEVEL"

        player = (await client.get("/v1/player", headers=auth)).json()
        slot_id = player["slots"][0]["id"]
        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200

        async with SessionLocal() as session:
            crop = await session.scalar(
                select(CropProduction)
                .where(CropProduction.slot_id == uuid.UUID(slot_id))
                .where(CropProduction.harvested_at.is_(None))
            )
            assert crop is not None
            crop.ready_at = datetime.now(UTC) - timedelta(seconds=1)
            await session.commit()

        harvest = await client.post(f"/v1/production/slots/{slot_id}/harvest", headers=auth)
        assert harvest.status_code == 200
        assert harvest.json()["yield_quantity"] == 4
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_capacity_upgrade_spends_cash_and_adds_a_slot(client: AsyncClient):
    email = f"p3-capacity-upgrade-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        initial_state = (await client.get("/v1/player", headers=auth)).json()
        assert len(initial_state["slots"]) == 3

        expansion = next(
            upgrade
            for upgrade in initial_state["upgrades"]
            if upgrade["key"] == "starter-room-expansion"
        )
        assert expansion["effects"]["slot_capacity_bonus"] == 1
        assert expansion["can_purchase"] is False

        await _grant_cash(email, 120)

        purchased = await client.post(f"/v1/upgrades/{expansion['key']}/purchase", headers=auth)
        assert purchased.status_code == 200
        purchase_body = purchased.json()
        assert purchase_body["cash_delta"] == -120
        assert purchase_body["cash_balance"] == 0
        assert purchase_body["upgrade"]["effects"]["slot_capacity_bonus"] == 1
        assert purchase_body["economy_summary"]["burned"] == 120

        expanded_state = (await client.get("/v1/player", headers=auth)).json()
        assert [slot["slot_index"] for slot in expanded_state["slots"]] == [0, 1, 2, 3]

        duplicate = await client.post(f"/v1/upgrades/{expansion['key']}/purchase", headers=auth)
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "UPGRADE_MAX_LEVEL"
    finally:
        await _cleanup(email)
