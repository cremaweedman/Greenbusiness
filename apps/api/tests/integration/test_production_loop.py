from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import CropProduction, ProductionSlot, User
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
            "display_name": "Grower",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_production_loop_persists_harvests_once_and_updates_inventory(client: AsyncClient):
    email = f"p2-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        player = await client.get("/v1/player", headers=auth)
        assert player.status_code == 200
        state = player.json()
        assert [variety["key"] for variety in state["starter_varieties"]] == [
            "aurora-drift",
            "ember-leaf",
            "moon-sprout",
        ]
        assert len(state["slots"]) == 3
        assert state["tutorial_step"] == 0
        assert state["tutorial_completed"] is False
        slot_id = state["slots"][0]["id"]

        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200
        planted_slot = planted.json()
        assert planted_slot["status"] == "planted"
        assert planted_slot["crop"]["variety_key"] == "aurora-drift"
        assert planted_slot["crop"]["is_ready"] is False

        replayed_player = await client.get("/v1/player", headers=auth)
        replayed_state = replayed_player.json()
        replayed_slot = replayed_state["slots"][0]
        assert replayed_slot["crop"]["id"] == planted_slot["crop"]["id"]
        assert replayed_slot["crop"]["ready_at"] == planted_slot["crop"]["ready_at"]
        assert replayed_state["tutorial_step"] == 1
        assert replayed_state["tutorial_completed"] is False

        occupied = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "ember-leaf"},
        )
        assert occupied.status_code == 409
        assert occupied.json()["error"]["code"] == "PRODUCTION_SLOT_OCCUPIED"

        early = await client.post(f"/v1/production/slots/{slot_id}/harvest", headers=auth)
        assert early.status_code == 409
        assert early.json()["error"]["code"] == "PRODUCTION_CROP_NOT_READY"

        cared = await client.post(f"/v1/production/slots/{slot_id}/care", headers=auth)
        assert cared.status_code == 200
        assert cared.json()["crop"]["cared_at"] is not None
        after_care = await client.get("/v1/player", headers=auth)
        assert after_care.json()["tutorial_step"] == 2

        async with SessionLocal() as session:
            slot_uuid = uuid.UUID(slot_id)
            crop = await session.scalar(
                select(CropProduction)
                .where(CropProduction.slot_id == slot_uuid)
                .where(CropProduction.harvested_at.is_(None))
            )
            assert crop is not None
            crop.ready_at = datetime.now(UTC) - timedelta(seconds=1)
            await session.commit()

        ready_player = await client.get("/v1/player", headers=auth)
        assert ready_player.json()["slots"][0]["status"] == "ready"

        harvest = await client.post(f"/v1/production/slots/{slot_id}/harvest", headers=auth)
        assert harvest.status_code == 200
        harvest_body = harvest.json()
        assert harvest_body["slot"]["status"] == "available"
        assert harvest_body["yield_quantity"] == 4
        assert harvest_body["quality"] == "cared"
        assert harvest_body["xp_reward"] == 20
        assert harvest_body["harvested_item"]["quantity"] == 4

        duplicate = await client.post(f"/v1/production/slots/{slot_id}/harvest", headers=auth)
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "PRODUCTION_SLOT_EMPTY"

        final_player = await client.get("/v1/player", headers=auth)
        final_state = final_player.json()
        assert final_state["xp"] == 20
        assert final_state["tutorial_step"] == 3
        assert final_state["tutorial_completed"] is True
        assert final_state["inventory"] == [
            {
                "item_key": "starter_crop.aurora-drift",
                "display_name": "Aurora Drift",
                "quantity": 4,
            }
        ]

        async with SessionLocal() as session:
            slot = await session.get(ProductionSlot, uuid.UUID(slot_id))
            assert slot is not None
            assert slot.status == "available"
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_production_rejects_unknown_variety(client: AsyncClient):
    email = f"p2-invalid-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}
        player = (await client.get("/v1/player", headers=auth)).json()

        response = await client.post(
            f"/v1/production/slots/{player['slots'][0]['id']}/plant",
            headers=auth,
            json={"variety_key": "real-world-name"},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "PRODUCTION_VARIETY_INVALID"
    finally:
        await _cleanup(email)
