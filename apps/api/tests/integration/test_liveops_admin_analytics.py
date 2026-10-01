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
            "seasons": {},
            "featured_traits": ["fast"] if production_enabled else [],
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
            "content_toggles": {"missions_v2": True},
            "contract_multipliers": {"default_cash": 1.0},
            "event_windows": {},
            "notification_copy": {},
            "experiments": {"starter_offer": ["control", "boosted"]},
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
        player_body = player.json()
        user_id = player_body["user_id"]
        slot_id = player_body["slots"][0]["id"]

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

        assignments = await client.get("/v1/liveops/experiments", headers=auth)
        assert assignments.status_code == 200
        assert assignments.json()["assignments"]["starter_offer"] in {"control", "boosted"}

        rollback = await client.post(
            "/v1/admin/config/rollback",
            headers=admin,
            json={"source_version": disabled_version},
        )
        assert rollback.status_code == 200
        assert rollback.json()["restored_from_version"] == disabled_version

        restored_enabled = await client.post(
            "/v1/admin/config/publish",
            headers=admin,
            json=_config(production_enabled=True),
        )
        assert restored_enabled.status_code == 200

        grant = await client.post(
            "/v1/admin/cash/grant",
            headers=admin,
            json={"user_id": user_id, "amount": 75, "reason": "integration grant"},
        )
        assert grant.status_code == 200
        assert grant.json()["cash_delta"] == 75

        revoke = await client.post(
            "/v1/admin/cash/revoke",
            headers=admin,
            json={"user_id": user_id, "amount": 25, "reason": "integration revoke"},
        )
        assert revoke.status_code == 200
        assert revoke.json()["cash_delta"] == -25

        ledger = await client.get(f"/v1/admin/ledger?user_id={user_id}", headers=admin)
        assert ledger.status_code == 200
        assert any(entry["source_or_sink"] == "admin_grant" for entry in ledger.json())

        dashboard = await client.get("/v1/admin/dashboards/economy", headers=admin)
        assert dashboard.status_code == 200
        assert dashboard.json()["wallet_distribution"]

        async with SessionLocal() as session:
            audit = await session.scalar(
                select(AuditEvent).where(AuditEvent.event_type == "admin.liveops_config_rolled_back")
            )
            grant_audit = await session.scalar(
                select(AuditEvent).where(AuditEvent.event_type == "admin.cash_granted")
            )
            analytics = await session.scalar(
                select(AnalyticsEvent).where(AnalyticsEvent.event_name == "auth.user_registered")
            )
            assert audit is not None
            assert grant_audit is not None
            assert analytics is not None
            assert "email" not in analytics.payload
    finally:
        await _cleanup(email)
