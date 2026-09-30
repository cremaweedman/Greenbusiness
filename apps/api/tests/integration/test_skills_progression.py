from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import CropProduction, Progression, User
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
            "display_name": "Skiller",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


async def _grant_skill_point(email: str) -> None:
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        assert user is not None
        progression = await session.scalar(select(Progression).where(Progression.user_id == user.id))
        assert progression is not None
        progression.skill_points = 1
        await session.commit()


@pytest.mark.asyncio
async def test_skill_allocation_changes_cared_harvest_and_respec_refunds(client: AsyncClient):
    email = f"p3-skill-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}

        denied = await client.post("/v1/skills/botany-careful-hands/allocate", headers=auth)
        assert denied.status_code == 409
        assert denied.json()["error"]["code"] == "SKILL_POINTS_INSUFFICIENT"

        await _grant_skill_point(email)
        allocated = await client.post("/v1/skills/botany-careful-hands/allocate", headers=auth)
        assert allocated.status_code == 200
        assert allocated.json()["skill"]["rank"] == 1
        assert allocated.json()["progression"]["skill_points"] == 0

        player = (await client.get("/v1/player", headers=auth)).json()
        assert player["skills"][0]["rank"] == 1
        slot_id = player["slots"][0]["id"]

        planted = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert planted.status_code == 200
        cared = await client.post(f"/v1/production/slots/{slot_id}/care", headers=auth)
        assert cared.status_code == 200

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
        assert harvest.json()["yield_quantity"] == 5

        respec = await client.post("/v1/skills/respec", headers=auth)
        assert respec.status_code == 200
        assert respec.json()["progression"]["skill_points"] == 1
        assert all(skill["rank"] == 0 for skill in respec.json()["skills"])
    finally:
        await _cleanup(email)
