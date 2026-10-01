from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import User
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


@pytest.mark.asyncio
async def test_decoration_purchase_is_ledger_backed_and_equip_is_persistent(client: AsyncClient):
    email = f"p10-decor-{uuid.uuid4()}@example.com"
    try:
        register = await client.post(
            "/v1/auth/register",
            json={"email": email, "password": "A-strong-password-789", "display_name": "Decorator"},
        )
        auth = {"Authorization": f"Bearer {register.json()['access_token']}"}

        before = await client.get("/v1/decorations/me", headers=auth)
        assert before.status_code == 200
        assert len(before.json()["items"]) == 40
        assert before.json()["cash"] == 500

        purchase = await client.post(
            "/v1/decorations/warm-lantern/purchase",
            headers={**auth, "Idempotency-Key": str(uuid.uuid4())},
        )
        assert purchase.status_code == 200
        assert purchase.json()["cash"] == 380
        assert purchase.json()["item"]["owned"] is True

        equip = await client.put(
            "/v1/decorations/warm-lantern/equip",
            headers=auth,
            json={"slot_index": 0},
        )
        assert equip.status_code == 200
        assert equip.json()["slot_index"] == 0

        after = (await client.get("/v1/decorations/me", headers=auth)).json()
        item = next(item for item in after["items"] if item["key"] == "warm-lantern")
        assert item["equipped_slot"] == 0
    finally:
        await _cleanup(email)
