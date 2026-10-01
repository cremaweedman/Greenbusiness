from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.db.models import (
    AuthSession,
    Business,
    InventoryContainer,
    PlayerProfile,
    ProductionSlot,
    Progression,
    Room,
    User,
)
from app.db.session import SessionLocal
from app.main import app
from app.security import hash_refresh_token


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
async def test_register_bootstrap_refresh_rotation_and_logout(client: AsyncClient):
    email = f"p1-{uuid.uuid4()}@example.com"
    password = "A-strong-password-123"

    try:
        register = await client.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "display_name": "Starter"},
        )
        assert register.status_code == 201
        first_access = register.json()["access_token"]
        first_refresh = client.cookies.get("gb_refresh")
        assert first_refresh

        player = await client.get(
            "/v1/player",
            headers={"Authorization": f"Bearer {first_access}"},
        )
        assert player.status_code == 200
        state = player.json()
        assert state["server_time"]
        assert state["email"] == email
        assert state["display_name"] == "Starter"
        assert state["room_slug"] == "starter-growroom"
        assert state["level"] == 1
        assert state["xp"] == 0
        assert state["tutorial_step"] == 0
        assert state["tutorial_completed"] is False
        assert len(state["slots"]) == 3

        duplicate = await client.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "display_name": "Duplicate"},
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "AUTH_EMAIL_EXISTS"

        async with SessionLocal() as session:
            user = await session.scalar(select(User).where(User.email == email))
            assert user is not None
            assert user.password_hash != password
            assert await session.scalar(
                select(func.count()).select_from(PlayerProfile).where(PlayerProfile.user_id == user.id)
            ) == 1
            business = await session.scalar(select(Business).where(Business.user_id == user.id))
            progression = await session.scalar(select(Progression).where(Progression.user_id == user.id))
            inventory = await session.scalar(
                select(InventoryContainer).where(InventoryContainer.user_id == user.id)
            )
            assert business is not None
            assert progression is not None
            assert inventory is not None
            room = await session.scalar(select(Room).where(Room.business_id == business.id))
            assert room is not None
            slot_count = await session.scalar(
                select(func.count()).select_from(ProductionSlot).where(ProductionSlot.room_id == room.id)
            )
            assert slot_count == 3

        refresh = await client.post("/v1/auth/refresh")
        assert refresh.status_code == 200
        second_refresh = client.cookies.get("gb_refresh")
        assert second_refresh and second_refresh != first_refresh

        async with SessionLocal() as session:
            old_session = await session.scalar(
                select(AuthSession).where(
                    AuthSession.refresh_token_hash == hash_refresh_token(first_refresh)
                )
            )
            assert old_session is not None
            assert old_session.revoked_at is not None

        old_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")
        try:
            old_client.cookies.set("gb_refresh", first_refresh)
            replay = await old_client.post("/v1/auth/refresh")
            assert replay.status_code == 401
            assert replay.json()["error"]["code"] == "AUTH_REFRESH_INVALID"
        finally:
            await old_client.aclose()

        logout = await client.post("/v1/auth/logout")
        assert logout.status_code == 204

        after_logout = await client.post("/v1/auth/refresh")
        assert after_logout.status_code == 401
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_login_recovers_same_player_state(client: AsyncClient):
    email = f"login-{uuid.uuid4()}@example.com"
    password = "A-strong-password-456"
    try:
        register = await client.post(
            "/v1/auth/register",
            json={"email": email, "password": password, "display_name": "Persistent"},
        )
        assert register.status_code == 201
        access = register.json()["access_token"]
        before = (
            await client.get("/v1/player", headers={"Authorization": f"Bearer {access}"})
        ).json()

        await client.post("/v1/auth/logout")
        login = await client.post("/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200
        after = (
            await client.get(
                "/v1/player",
                headers={"Authorization": f"Bearer {login.json()['access_token']}"},
            )
        ).json()

        assert after["user_id"] == before["user_id"]
        assert after["business_id"] == before["business_id"]
        assert after["room_id"] == before["room_id"]
        assert [slot["id"] for slot in after["slots"]] == [slot["id"] for slot in before["slots"]]
    finally:
        await _cleanup(email)


@pytest.mark.asyncio
async def test_dev_creator_access_creates_reusable_passwordless_session(client: AsyncClient):
    email = "creator@greenbusiness.local"

    try:
        first = await client.post("/v1/auth/dev/creator")
        assert first.status_code == 200
        first_access = first.json()["access_token"]
        assert client.cookies.get("gb_refresh")

        player = await client.get(
            "/v1/player",
            headers={"Authorization": f"Bearer {first_access}"},
        )
        assert player.status_code == 200
        state = player.json()
        assert state["email"] == email
        assert state["display_name"] == "Creator"
        assert state["cash"] == 500

        second = await client.post("/v1/auth/dev/creator")
        assert second.status_code == 200
        second_player = await client.get(
            "/v1/player",
            headers={"Authorization": f"Bearer {second.json()['access_token']}"},
        )
        assert second_player.status_code == 200
        assert second_player.json()["user_id"] == state["user_id"]

        async with SessionLocal() as session:
            assert (
                await session.scalar(
                    select(func.count()).select_from(User).where(User.email == email)
                )
            ) == 1
    finally:
        await _cleanup(email)
