from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings, settings
from app.rate_limit import RateLimitExceeded, RateLimitRule, enforce_rate_limit, reset_memory_rate_limits
from app.security import AdminPrincipal, require_admin_role


def test_production_rejects_insecure_defaults():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env="production",
            jwt_secret="development-only-change-me",
            admin_api_key="short",
            admin_jwt_secret="short",
            cookie_secure=False,
            creator_access_enabled=True,
            sandbox_monetization_enabled=True,
            sandbox_rewarded_ads_enabled=True,
            rate_limit_enabled=False,
            rate_limit_backend="memory",
            push_token_encryption_key="",
        )


def test_admin_roles_enforce_operator_boundary():
    require_admin_role(AdminPrincipal(actor_id="viewer", role="viewer"), minimum="viewer")
    with pytest.raises(Exception):
        require_admin_role(AdminPrincipal(actor_id="viewer", role="viewer"), minimum="operator")


@pytest.mark.asyncio
async def test_memory_rate_limit_blocks_after_threshold(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_backend", "memory")
    await reset_memory_rate_limits()
    rule = RateLimitRule("unit-test", 2, 60)
    await enforce_rate_limit(rule, subject="subject-a")
    await enforce_rate_limit(rule, subject="subject-a")
    with pytest.raises(RateLimitExceeded):
        await enforce_rate_limit(rule, subject="subject-a")
    await reset_memory_rate_limits()
