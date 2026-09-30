from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.db.models import AnalyticsEvent, AuditEvent, User
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
            "display_name": "Operator",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def _config(*, production_enabled: bool) -> dict[str, object]:
    return {
        "config": {
            "feature_flags": {
                "production": production_enabled,
                "contracts": True,
                "upgrades": True,
                "missions": True,
            },
            "kill_switches": {
                "production": False,
                "contracts": False,
                "upgrades": False,
                "missions": False,
            },
            "contract_multipliers": {"default_cash": 1.0},
            "event_windows": {},
            "notification_copy": {},
            "experiments": {},
        }
    }


@pytest.mark.asyncio
async def test_liveops_publish_disable_and_rollback_are_audited(client: AsyncClient):
    email = f"p5-liveops-{uuid.uuid4()}@example.com"
    try:
        access_token = await _register(client, email)
        auth = {"Authorization": f"Bearer {access_token}"}
        admin = {"X-Admin-Key": settings.admin_api_key}

        player = await client.get("/v1/player", headers=auth)
        assert player.status_code == 200
        slot_id = player.json()["slots"][0]["id"]

        disabled = await client.post(
            "/v1/admin/config/publish",
            headers=admin,
            json=_config(production_enabled=False),
        )
        assert disabled.status_code == 200
        disabled_version = disabled.json()["version"]

        blocked = await client.post(
            f"/v1/production/slots/{slot_id}/plant",
            headers=auth,
            json={"variety_key": "aurora-drift"},
        )
        assert blocked.status_code == 503
        assert blocked.json()["error"]["code"] == "FEATURE_DISABLED"

        enabled = await client.post(
            "/v1/admin/config/publish",
            headers=admin,
            json=_config(production_enabled=True),
        )
        assert enabled.status_code == 200

        rollback = await client.post(
            "/v1/admin/config/rollback",
            headers=admin,
            json={"source_version": disabled_version},
        )
        assert rollback.status_code == 200
        assert rollback.json()["restored_from_version"] == disabled_version

        async with SessionLocal() as session:
            audit = await session.scalar(
                select(AuditEvent).where(AuditEvent.event_type == "admin.liveops_config_rolled_back")
            )
            analytics = await session.scalar(
                select(AnalyticsEvent).where(AnalyticsEvent.event_name == "auth.user_registered")
            )
            assert audit is not None
            assert analytics is not None
            assert "email" not in analytics.payload
    finally:
        await _cleanup(email)
