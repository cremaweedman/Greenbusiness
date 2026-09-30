from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import MissionPoolAssignment, User
from app.db.session import SessionLocal
from app.main import app
from app.mission_service import meta_state, record_domain_event


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


@pytest.mark.asyncio
async def test_period_assignments_persist_and_mastery_cosmetics_are_non_economic(
    client: AsyncClient,
):
    email = f"p4-m2-{uuid.uuid4()}@example.com"
    try:
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": email,
                "password": "A-strong-password-p4-m2",
                "display_name": "Narrative Tester",
            },
        )
        assert response.status_code == 201

        fixed = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)
        next_day = fixed + timedelta(days=1)

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None

            first = await meta_state(
                session,
                user.id,
                now=fixed,
                persist_bootstrap=True,
            )
            assert len(first.daily_mission_keys) == 2
            assert len(first.weekly_mission_keys) == 3

            same_period = await meta_state(
                session,
                user.id,
                now=fixed,
                persist_bootstrap=True,
            )
            assert same_period.daily_mission_keys == first.daily_mission_keys
            assert same_period.weekly_mission_keys == first.weekly_mission_keys

            next_period = await meta_state(
                session,
                user.id,
                now=next_day,
                persist_bootstrap=True,
            )
            assert len(next_period.daily_mission_keys) == 2
            assert next_period.weekly_mission_keys == first.weekly_mission_keys

            assignments = (
                await session.scalars(
                    select(MissionPoolAssignment)
                    .where(MissionPoolAssignment.user_id == user.id)
                    .order_by(
                        MissionPoolAssignment.period_type,
                        MissionPoolAssignment.period_key,
                        MissionPoolAssignment.slot_index,
                    )
                )
            ).all()
            assert len(assignments) == 7
            assert {item.period_type for item in assignments} == {"daily", "weekly"}

            accepted = await record_domain_event(
                session,
                user_id=user.id,
                event_key="mastery:p4-m2-threshold",
                event_type="harvest",
                variety_key="aurora-drift",
                mastery_quantity=55,
                request_id="test",
            )
            assert accepted is True
            await session.commit()

            state = await meta_state(session, user.id, now=fixed)
            mastery = next(
                item for item in state.mastery if item.variety_key == "aurora-drift"
            )
            assert mastery.points == 55
            assert mastery.tier == 3
            assert mastery.next_threshold is None
            assert len(mastery.unlocked_cosmetic_keys) == 3

            before_replay = list(mastery.unlocked_cosmetic_keys)
            replay = await record_domain_event(
                session,
                user_id=user.id,
                event_key="mastery:p4-m2-threshold",
                event_type="harvest",
                variety_key="aurora-drift",
                mastery_quantity=55,
                request_id="test",
            )
            assert replay is False
            await session.commit()

            replay_state = await meta_state(session, user.id, now=fixed)
            replay_mastery = next(
                item for item in replay_state.mastery if item.variety_key == "aurora-drift"
            )
            assert replay_mastery.points == 55
            assert replay_mastery.unlocked_cosmetic_keys == before_replay
    finally:
        await _cleanup(email)
