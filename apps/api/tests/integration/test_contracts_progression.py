from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import (
    CropProduction,
    PlayerContract,
    PlayerSkillBranch,
    Progression,
    User,
)
from app.db.session import SessionLocal
from app.economy_service import generate_contract_offers
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
            "password": "A-strong-password-p3m2",
            "display_name": "Progression",
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


def test_contract_offers_are_deterministic_inside_refresh_bucket():
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    first = datetime(2026, 9, 30, 12, 1, tzinfo=UTC)
    same_bucket = datetime(2026, 9, 30, 15, 59, tzinfo=UTC)
    next_bucket = datetime(2026, 9, 30, 16, 1, tzinfo=UTC)

    offers_a = generate_contract_offers(
        user_id=user_id,
        level=1,
        reputation=0,
        now=first,
    )
    offers_b = generate_contract_offers(
        user_id=user_id,
        level=1,
        reputation=0,
        now=same_bucket,
    )
    offers_c = generate_contract_offers(
        user_id=user_id,
        level=1,
        reputation=0,
        now=next_bucket,
    )

    assert len(offers_a) == 4
    assert sum(not offer.specialized for offer in offers_a) == 3
    assert sum(offer.specialized for offer in offers_a) == 1
    assert [offer.offer_id for offer in offers_a] == [offer.offer_id for offer in offers_b]
    assert [offer.offer_id for offer in offers_a] != [offer.offer_id for offer in offers_c]
    assert offers_a[0].key == "neighborhood-sampler"
    assert offers_a[-1].locked is True


@pytest.mark.asyncio
async def test_player_bootstraps_progression_and_skill_hooks(client: AsyncClient):
    email = f"p3m2-bootstrap-{uuid.uuid4()}@example.com"
    try:
        access = await _register(client, email)
        state = (
            await client.get(
                "/v1/player",
                headers={"Authorization": f"Bearer {access}"},
            )
        ).json()

        assert state["level"] == 1
        assert state["next_level_xp"] == 100
        assert state["reputation"] == 0
        assert state["skill_points_unspent"] == 0
        assert {branch["branch"] for branch in state["skill_branches"]} == {
            "botany",
            "commerce",
            "operations",
        }
        assert "contracts-standard" in state["unlocked_keys"]
        assert len(state["contract_offers"]) == 4
        assert state["contract_refresh_at"] > state["server_time"]
        assert state["inventory_lots"] == []
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_active_contract_limit_cannot_be_bypassed(client: AsyncClient):
    email = f"p3m2-limit-{uuid.uuid4()}@example.com"
    try:
        access = await _register(client, email)
        auth = {"Authorization": f"Bearer {access}"}

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            progression = await session.scalar(
                select(Progression).where(Progression.user_id == user.id)
            )
            assert progression is not None
            progression.level = 5
            progression.reputation = 100
            await session.commit()

        state = (await client.get("/v1/player", headers=auth)).json()
        offers = state["contract_offers"]
        assert len(offers) == 4
        assert all(offer["locked"] is False for offer in offers)

        for offer in offers[:3]:
            accepted = await client.post(
                f"/v1/economy/offers/{offer['offer_id']}/accept",
                headers=auth,
            )
            assert accepted.status_code == 200

        rejected = await client.post(
            f"/v1/economy/offers/{offers[3]['offer_id']}/accept",
            headers=auth,
        )
        assert rejected.status_code == 409
        assert rejected.json()["error"]["code"] == "CONTRACT_ACTIVE_LIMIT"

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            active = (
                await session.scalars(
                    select(PlayerContract)
                    .where(PlayerContract.user_id == user.id)
                    .where(PlayerContract.status == "active")
                )
            ).all()
            assert len(active) == 3
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_harvest_quality_and_level_progression_persist(client: AsyncClient):
    email = f"p3m2-level-{uuid.uuid4()}@example.com"
    try:
        access = await _register(client, email)
        auth = {"Authorization": f"Bearer {access}"}
        state = (await client.get("/v1/player", headers=auth)).json()
        slot_id = state["slots"][0]["id"]

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            progression = await session.scalar(
                select(Progression).where(Progression.user_id == user.id)
            )
            assert progression is not None
            progression.xp = 95
            await session.commit()

        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200
        cared = await client.post(
            f"/v1/production/slots/{slot_id}/care",
            headers=auth,
        )
        assert cared.status_code == 200
        await _force_ready(slot_id)

        harvested = await client.post(
            f"/v1/production/slots/{slot_id}/harvest",
            headers=auth,
        )
        assert harvested.status_code == 200
        body = harvested.json()
        assert body["quality"] == "cared"
        assert body["inventory_lots"] == [
            {
                "item_key": "starter_crop.aurora-drift",
                "display_name": "Aurora Drift",
                "quality": "cared",
                "quantity": 4,
            }
        ]

        after = (await client.get("/v1/player", headers=auth)).json()
        assert after["level"] == 2
        assert after["skill_points_unspent"] == 1
        assert after["next_level_xp"] is not None

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            branches = (
                await session.scalars(
                    select(PlayerSkillBranch)
                    .where(PlayerSkillBranch.user_id == user.id)
                    .order_by(PlayerSkillBranch.branch)
                )
            ).all()
            assert len(branches) == 3
            assert all(branch.points == 0 for branch in branches)
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_skill_tree_allocation_is_server_authoritative(client: AsyncClient):
    email = f"p10-skills-{uuid.uuid4()}@example.com"
    try:
        access = await _register(client, email)
        auth = {"Authorization": f"Bearer {access}"}

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            progression = await session.scalar(
                select(Progression).where(Progression.user_id == user.id)
            )
            assert progression is not None
            progression.skill_points_unspent = 1
            await session.commit()

        allocated = await client.post(
            "/v1/economy/skills/botany/allocate",
            headers=auth,
        )
        assert allocated.status_code == 200
        assert allocated.json()["branch"] == "botany"
        assert allocated.json()["points"] == 1
        assert allocated.json()["max_points"] == 3

        no_points = await client.post(
            "/v1/economy/skills/commerce/allocate",
            headers=auth,
        )
        assert no_points.status_code == 409
        assert no_points.json()["error"]["code"] == "SKILL_POINTS_EMPTY"

        state = (await client.get("/v1/player", headers=auth)).json()
        botany = next(item for item in state["skill_branches"] if item["branch"] == "botany")
        assert botany["points"] == 1
        assert state["skill_points_unspent"] == 0
    finally:
        await _cleanup(email)
