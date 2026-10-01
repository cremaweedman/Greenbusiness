from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.config import settings
from app.db.models import ClubContribution, ClubRewardClaim, EconomyLedger, User
from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(autouse=True)
def admin_runtime(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "test")
    monkeypatch.setattr(settings, "admin_api_key", "social-admin-bootstrap-key-1234567890")
    monkeypatch.setattr(settings, "admin_jwt_secret", "social-admin-jwt-secret-123456789012345")
    monkeypatch.setattr(settings, "admin_actor_id", "social-test-admin")
    monkeypatch.setattr(settings, "admin_role", "superadmin")


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


async def _register(client: AsyncClient, email: str, display_name: str) -> str:
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "password": "A-strong-password-246",
            "display_name": display_name,
        },
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def _config(*, clubs_enabled: bool) -> dict[str, object]:
    return {
        "config": {
            "seasons": {},
            "featured_traits": [],
            "feature_flags": {
                "production": True,
                "contracts": True,
                "upgrades": True,
                "missions": True,
                "clubs": clubs_enabled,
            },
            "kill_switches": {
                "production": False,
                "contracts": False,
                "upgrades": False,
                "missions": False,
                "clubs": False,
            },
            "content_toggles": {"missions_v2": True, "clubs_v1": clubs_enabled},
            "contract_multipliers": {"default_cash": 1.0, "default_reputation": 1.0},
            "event_windows": {},
            "notification_copy": {},
            "experiments": {},
        }
    }


@pytest.mark.asyncio
async def test_social_club_lifecycle_is_idempotent_limited_and_rewarded(client: AsyncClient):
    owner_email = f"p6-owner-{uuid.uuid4()}@example.com"
    member_email = f"p6-member-{uuid.uuid4()}@example.com"
    try:
        owner_token = await _register(client, owner_email, "Club Owner")
        member_token = await _register(client, member_email, "Club Mate")
        owner = {"Authorization": f"Bearer {owner_token}"}
        member = {"Authorization": f"Bearer {member_token}"}

        owner_social = await client.get("/v1/social/me", headers=owner)
        assert owner_social.status_code == 200
        member_social = await client.get("/v1/social/me", headers=member)
        assert member_social.status_code == 200
        member_code = member_social.json()["profile"]["friend_code"]
        assert member_social.json()["profile"]["deep_link"].endswith(member_code)

        friend = await client.post(
            "/v1/social/friends/redeem",
            headers=owner,
            json={"friend_code": member_code},
        )
        assert friend.status_code == 200
        assert friend.json()["friend_code"] == member_code

        club = await client.post("/v1/clubs", headers=owner, json={"name": "Verdant Crew"})
        assert club.status_code == 201
        club_body = club.json()
        club_id = club_body["id"]
        assert club_body["member_count"] == 1
        assert club_body["max_members"] == 30
        assert club_body["objective"]["target_amount"] == 10

        invite = await client.post(
            f"/v1/clubs/{club_id}/invites",
            headers=owner,
            json={"friend_code": member_code},
        )
        assert invite.status_code == 201
        invite_id = invite.json()["id"]

        member_state = await client.get("/v1/social/me", headers=member)
        assert member_state.status_code == 200
        assert member_state.json()["pending_invites"][0]["id"] == invite_id

        joined = await client.post(f"/v1/clubs/invites/{invite_id}/accept", headers=member)
        assert joined.status_code == 200
        assert joined.json()["member_count"] == 2

        contribution = await client.post(
            f"/v1/clubs/{club_id}/contributions",
            headers=owner,
            json={"event_key": "manual:p6:one", "amount": 9, "contribution_type": "manual"},
        )
        assert contribution.status_code == 200
        assert contribution.json()["objective"]["progress_amount"] == 9

        replay = await client.post(
            f"/v1/clubs/{club_id}/contributions",
            headers=owner,
            json={"event_key": "manual:p6:one", "amount": 9, "contribution_type": "manual"},
        )
        assert replay.status_code == 200
        assert replay.json()["idempotent"] is True
        assert replay.json()["objective"]["progress_amount"] == 9

        owner_code = owner_social.json()["profile"]["friend_code"]
        assist = await client.post(
            f"/v1/clubs/{club_id}/assists",
            headers=member,
            json={"receiver_friend_code": owner_code, "assist_type": "care"},
        )
        assert assist.status_code == 200
        assert assist.json()["remaining_weekly_assists"] == 4

        duplicate_assist = await client.post(
            f"/v1/clubs/{club_id}/assists",
            headers=member,
            json={"receiver_friend_code": owner_code, "assist_type": "care"},
        )
        assert duplicate_assist.status_code == 409
        assert duplicate_assist.json()["error"]["code"] == "CLUB_ASSIST_DUPLICATE"

        completed_state = await client.get("/v1/social/me", headers=owner)
        assert completed_state.status_code == 200
        assert completed_state.json()["club"]["objective"]["status"] == "completed"
        assert completed_state.json()["club"]["objective"]["progress_amount"] == 10

        reaction = await client.post(
            f"/v1/clubs/{club_id}/reactions",
            headers=member,
            json={"target_type": "objective", "target_id": club_id, "reaction_key": "cheer"},
        )
        assert reaction.status_code == 200
        reaction_replay = await client.post(
            f"/v1/clubs/{club_id}/reactions",
            headers=member,
            json={"target_type": "objective", "target_id": club_id, "reaction_key": "cheer"},
        )
        assert reaction_replay.status_code == 200
        assert reaction_replay.json()["idempotent"] is True

        reward = await client.post(f"/v1/clubs/{club_id}/rewards/claim", headers=member)
        assert reward.status_code == 200
        assert reward.json()["cash_delta"] == 75
        reward_replay = await client.post(f"/v1/clubs/{club_id}/rewards/claim", headers=member)
        assert reward_replay.status_code == 200
        assert reward_replay.json()["idempotent"] is True
        assert reward_replay.json()["cash_delta"] == 0

        admin_bootstrap = await client.post(
            "/v1/admin/auth/token",
            headers={"X-Admin-Key": settings.admin_api_key},
        )
        assert admin_bootstrap.status_code == 200
        admin = {"Authorization": f"Bearer {admin_bootstrap.json()['access_token']}"}
        disabled = await client.post(
            "/v1/admin/config/publish",
            headers=admin,
            json=_config(clubs_enabled=False),
        )
        assert disabled.status_code == 200
        disabled_social = await client.get("/v1/social/me", headers=owner)
        assert disabled_social.status_code == 503
        assert disabled_social.json()["error"]["code"] == "FEATURE_DISABLED"
        restored = await client.post(
            "/v1/admin/config/publish",
            headers=admin,
            json=_config(clubs_enabled=True),
        )
        assert restored.status_code == 200

        async with SessionLocal() as session:
            assert await session.scalar(select(ClubContribution).where(ClubContribution.event_key == "manual:p6:one"))
            assert await session.scalar(select(ClubRewardClaim).where(ClubRewardClaim.user_id == uuid.UUID(joined.json()["members"][1]["user_id"])))
            ledgers = (
                await session.scalars(
                    select(EconomyLedger).where(EconomyLedger.source_or_sink == "club_reward")
                )
            ).all()
            assert any(entry.amount == 75 for entry in ledgers)
    finally:
        await _cleanup(owner_email, member_email)
