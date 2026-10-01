from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.db.models import User
from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def alpha_admin_runtime(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "admin_api_key", "alpha-admin-bootstrap-key-1234567890123")
    monkeypatch.setattr(settings, "admin_jwt_secret", "alpha-admin-jwt-secret-12345678901234567")
    monkeypatch.setattr(settings, "admin_actor_id", "alpha-admin")
    monkeypatch.setattr(settings, "admin_role", "superadmin")


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
async def test_alpha_feedback_triage_and_dashboard(client: AsyncClient):
    email = f"p10-alpha-{uuid.uuid4()}@example.com"
    try:
        register = await client.post(
            "/v1/auth/register",
            json={
                "email": email,
                "password": "A-strong-password-789",
                "display_name": "Alpha Tester",
            },
        )
        assert register.status_code == 201
        auth = {"Authorization": f"Bearer {register.json()['access_token']}"}

        feedback = await client.post(
            "/v1/alpha/feedback",
            headers=auth,
            json={
                "kind": "bug",
                "severity": "major",
                "category": "production",
                "message": "Timer copy was confusing on return.",
                "build_sha": "2ea06e03148efc608601e78ab142eef9bf77f548",
                "liveops_version": 0,
            },
        )
        assert feedback.status_code == 201
        feedback_id = feedback.json()["id"]
        assert feedback.json()["status"] == "new"

        bootstrap = await client.post(
            "/v1/admin/auth/token",
            headers={"X-Admin-Key": settings.admin_api_key},
        )
        assert bootstrap.status_code == 200
        admin = {"Authorization": f"Bearer {bootstrap.json()['access_token']}"}

        queue = await client.get("/v1/admin/alpha/feedback?status=new", headers=admin)
        assert queue.status_code == 200
        assert any(item["id"] == feedback_id for item in queue.json())

        triaged = await client.patch(
            f"/v1/admin/alpha/feedback/{feedback_id}",
            headers=admin,
            json={"status": "triaged", "severity": "minor"},
        )
        assert triaged.status_code == 200
        assert triaged.json()["status"] == "triaged"
        assert triaged.json()["severity"] == "minor"
        assert triaged.json()["triaged_by"] == "alpha-admin"

        dashboard = await client.get("/v1/admin/alpha/dashboard", headers=admin)
        assert dashboard.status_code == 200
        body = dashboard.json()
        assert body["cohort_size"] >= 1
        assert body["feedback_new"] == 0
    finally:
        await _cleanup(email)
