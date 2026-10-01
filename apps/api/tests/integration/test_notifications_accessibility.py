from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.models import PushToken, User
from app.db.session import SessionLocal
from app.main import app
from app.notification_service import decrypt_push_token


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as value:
        yield value


async def _cleanup(*emails: str) -> None:
    async with SessionLocal() as session:
        for email in emails:
            user = await session.scalar(select(User).where(User.email == email))
            if user is not None:
                await session.delete(user)
        await session.commit()


async def _register(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "A-strong-password-852",
            "display_name": "Notifier",
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_notification_preferences_tokens_and_platform_readiness_are_safe(
    client: AsyncClient,
):
    email = f"p8-user-{uuid.uuid4()}@example.com"
    try:
        token = await _register(client, email)
        headers = {"Authorization": f"Bearer {token}"}

        initial = await client.get("/v1/notifications/me", headers=headers)
        assert initial.status_code == 200
        initial_body = initial.json()
        assert initial_body["preferences"]["production_enabled"] is True
        assert initial_body["preferences"]["events_enabled"] is True
        assert initial_body["preferences"]["social_enabled"] is True
        assert initial_body["preferences"]["quiet_hours_start"] == "22:00"
        assert initial_body["preferences"]["quiet_hours_end"] == "08:00"
        assert initial_body["pwa"]["installable"] is True
        assert initial_body["pwa"]["offline_read_cache"] is True
        assert initial_body["deep_links"]["production"] == "greenbusiness://production"
        assert initial_body["push_tokens"] == []

        updated = await client.patch(
            "/v1/notifications/preferences",
            headers=headers,
            json={
                "production_enabled": False,
                "social_enabled": False,
                "quiet_hours_start": "21:30",
                "quiet_hours_end": "07:15",
                "timezone": "Europe/Madrid",
            },
        )
        assert updated.status_code == 200
        assert updated.json()["production_enabled"] is False
        assert updated.json()["social_enabled"] is False
        assert updated.json()["quiet_hours_start"] == "21:30"

        invalid_time = await client.patch(
            "/v1/notifications/preferences",
            headers=headers,
            json={"quiet_hours_start": "25:99"},
        )
        assert invalid_time.status_code == 400
        assert invalid_time.json()["error"]["code"] == "NOTIFICATION_TIME_INVALID"

        registered = await client.post(
            "/v1/notifications/push-tokens",
            headers=headers,
            json={"platform": "web", "token": "web-push-token-abcdef123456"},
        )
        assert registered.status_code == 201
        registered_body = registered.json()
        assert registered_body["platform"] == "web"
        assert registered_body["token_label"] == "…123456"
        assert registered_body["enabled"] is True

        replay = await client.post(
            "/v1/notifications/push-tokens",
            headers=headers,
            json={"platform": "web", "token": "web-push-token-abcdef123456"},
        )
        assert replay.status_code == 201
        assert replay.json()["id"] == registered_body["id"]
        assert replay.json()["enabled"] is True

        unsupported = await client.post(
            "/v1/notifications/push-tokens",
            headers=headers,
            json={"platform": "console", "token": "unsupported-token-abcdef"},
        )
        assert unsupported.status_code == 400
        assert unsupported.json()["error"]["code"] == "PUSH_PLATFORM_UNSUPPORTED"

        disabled = await client.post(
            f"/v1/notifications/push-tokens/{registered_body['id']}/disable",
            headers=headers,
        )
        assert disabled.status_code == 200
        assert disabled.json()["enabled"] is False

        final_state = await client.get("/v1/notifications/me", headers=headers)
        assert final_state.status_code == 200
        assert final_state.json()["push_tokens"][0]["enabled"] is False

        readiness = await client.get("/v1/platform/readiness")
        assert readiness.status_code == 200
        readiness_body = readiness.json()
        assert readiness_body["pwa_installable"] is True
        assert readiness_body["core_gameplay_requires_push"] is False
        assert readiness_body["punitive_return_mechanics"] is False
        assert readiness_body["ios_release_requires_policy_review"] is True
        assert "Trusted Web Activity" in readiness_body["android_packaging_path"]
        assert "policy review" in readiness_body["ios_packaging_path"]

        async with SessionLocal() as session:
            rows = (await session.scalars(select(PushToken))).all()
            assert "web-push-token-abcdef123456" not in {row.token_hash for row in rows}
            assert any(row.token_label == "…123456" for row in rows)
            assert all(row.token_ciphertext != "web-push-token-abcdef123456" for row in rows)
            assert any(decrypt_push_token(row) == "web-push-token-abcdef123456" for row in rows)
    finally:
        await _cleanup(email)
