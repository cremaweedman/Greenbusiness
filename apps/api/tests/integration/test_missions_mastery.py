from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import CropProduction, PlayerMission, PlayerVarietyMastery, User
from app.db.session import SessionLocal
from app.main import app
from app.mission_service import record_domain_event


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
            "password": "A-strong-password-p4",
            "display_name": "Mission Tester",
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
async def test_production_events_advance_missions_and_mastery_without_replay_rewards(
    client: AsyncClient,
):
    email = f"p4-{uuid.uuid4()}@example.com"

    try:
        token = await _register(client, email)
        auth = {"Authorization": f"Bearer {token}"}

        initial = (await client.get("/v1/player", headers=auth)).json()
        assert len(initial["missions"]) == 10
        assert initial["missions"][0]["status"] == "active"
        assert initial["missions"][1]["status"] == "locked"
        assert len(initial["contacts"]) == 2
        assert len(initial["daily_mission_keys"]) == 2
        assert len(initial["weekly_mission_keys"]) == 3

        slot_id = initial["slots"][0]["id"]
        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200

        after_plant = (await client.get("/v1/player", headers=auth)).json()
        assert after_plant["missions"][0]["status"] == "completed"
        assert after_plant["missions"][1]["status"] == "active"

        cared = await client.post(
            f"/v1/production/slots/{slot_id}/care",
            headers=auth,
        )
        assert cared.status_code == 200

        after_care = (await client.get("/v1/player", headers=auth)).json()
        assert after_care["missions"][1]["status"] == "completed"
        assert after_care["missions"][2]["status"] == "active"

        await _force_ready(slot_id)
        harvested = await client.post(
            f"/v1/production/slots/{slot_id}/harvest",
            headers=auth,
        )
        assert harvested.status_code == 200
        assert harvested.json()["yield_quantity"] == 4

        state = (await client.get("/v1/player", headers=auth)).json()
        assert state["missions"][2]["status"] == "completed"
        assert state["missions"][3]["status"] == "active"
        assert state["cash"] == 550
        assert len(state["mastery"]) == 1
        mastery = state["mastery"][0]
        assert mastery["variety_key"] == "aurora-drift"
        assert mastery["harvest_quantity"] == 4
        assert mastery["contract_quantity"] == 0
        assert mastery["points"] == 4

        replay = await client.post(
            f"/v1/production/slots/{slot_id}/harvest",
            headers=auth,
        )
        assert replay.status_code == 409

        after_replay = (await client.get("/v1/player", headers=auth)).json()
        assert after_replay["cash"] == 550
        assert after_replay["mastery"][0]["points"] == 4
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_mission_event_receipts_prevent_duplicate_progress_and_mastery(client: AsyncClient):
    email = f"p4-idempotent-{uuid.uuid4()}@example.com"

    try:
        token = await _register(client, email)
        auth = {"Authorization": f"Bearer {token}"}

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None

            # Finish mission 1-3 and mission 4 with authoritative-style unique events.
            for index, event_type in enumerate(["plant", "care", "harvest"], start=1):
                await record_domain_event(
                    session,
                    user_id=user.id,
                    event_key=f"setup:{index}",
                    event_type=event_type,
                    request_id="test",
                )
                await session.commit()

            for index in range(3):
                await record_domain_event(
                    session,
                    user_id=user.id,
                    event_key=f"harvest-extra:{index}",
                    event_type="harvest",
                    request_id="test",
                )
                await session.commit()

            first_contract = await record_domain_event(
                session,
                user_id=user.id,
                event_key="contract:test-1",
                event_type="contract_complete",
                cash_earned=150,
                item_key="starter_crop.aurora-drift",
                contract_quantity=3,
                request_id="test",
            )
            await session.commit()
            assert first_contract is True

            duplicate_contract = await record_domain_event(
                session,
                user_id=user.id,
                event_key="contract:test-1",
                event_type="contract_complete",
                cash_earned=150,
                item_key="starter_crop.aurora-drift",
                contract_quantity=3,
                request_id="test",
            )
            await session.commit()
            assert duplicate_contract is False

            await record_domain_event(
                session,
                user_id=user.id,
                event_key="contract:test-2",
                event_type="contract_complete",
                cash_earned=100,
                request_id="test",
            )
            await session.commit()
            await record_domain_event(
                session,
                user_id=user.id,
                event_key="contract:test-3",
                event_type="contract_complete",
                cash_earned=100,
                request_id="test",
            )
            await session.commit()

            await record_domain_event(
                session,
                user_id=user.id,
                event_key="upgrade:wrong",
                event_type="upgrade_owned",
                upgrade_key="not-the-required-upgrade",
                request_id="test",
            )
            await session.commit()
            await record_domain_event(
                session,
                user_id=user.id,
                event_key="upgrade:starter-yield-boost",
                event_type="upgrade_owned",
                upgrade_key="starter-yield-boost",
                request_id="test",
            )
            await session.commit()

            mastery = await session.scalar(
                select(PlayerVarietyMastery)
                .where(PlayerVarietyMastery.user_id == user.id)
                .where(PlayerVarietyMastery.variety_key == "aurora-drift")
            )
            assert mastery is not None
            assert mastery.contract_quantity == 3

            missions = (
                await session.scalars(
                    select(PlayerMission)
                    .where(PlayerMission.user_id == user.id)
                    .order_by(PlayerMission.created_at, PlayerMission.mission_key)
                )
            ).all()
            by_key = {mission.mission_key: mission for mission in missions}
            assert by_key["first-client"].status == "completed"
            assert by_key["cashflow"].status == "completed"
            assert by_key["efficient-space"].status == "completed"

        player = (await client.get("/v1/player", headers=auth)).json()
        mastery_state = next(
            item for item in player["mastery"] if item["variety_key"] == "aurora-drift"
        )
        assert mastery_state["contract_quantity"] == 3
    finally:
        await _cleanup(email)
