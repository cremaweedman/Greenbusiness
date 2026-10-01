from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PRODUCTION_ENVS = {"production", "prod", "staging"}


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://greenbusiness:change-me@postgres:5432/greenbusiness"

    jwt_secret: str = "development-only-change-me"
    jwt_issuer: str = "greenbusiness"
    jwt_access_ttl_seconds: int = 900
    refresh_ttl_seconds: int = 2_592_000
    refresh_cookie_name: str = "gb_refresh"
    cookie_secure: bool = False

    admin_api_key: str = ""
    admin_jwt_secret: str = ""
    admin_actor_id: str = "bootstrap-admin"
    admin_role: str = "superadmin"
    admin_token_ttl_seconds: int = 900

    creator_access_enabled: bool = False
    creator_email: str = "creator@greenbusiness.local"
    creator_display_name: str = "Creator"

    sandbox_monetization_enabled: bool = False
    sandbox_rewarded_ads_enabled: bool = False

    redis_url: str = "redis://redis:6379/0"
    rate_limit_enabled: bool = False
    rate_limit_backend: str = "memory"

    push_token_encryption_key: str = ""
    analytics_request_sample_rate: float = 0.1

    storage_backend: str = "local"
    storage_local_path: str = "/data/greenbusiness"
    s3_endpoint: str | None = None
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def production_like(self) -> bool:
        return self.app_env.lower() in PRODUCTION_ENVS

    @model_validator(mode="after")
    def validate_security_defaults(self) -> Settings:
        if not 0 <= self.analytics_request_sample_rate <= 1:
            raise ValueError("ANALYTICS_REQUEST_SAMPLE_RATE must be between 0 and 1")
        if self.admin_role not in {"viewer", "operator", "superadmin"}:
            raise ValueError("ADMIN_ROLE must be viewer, operator or superadmin")
        if self.rate_limit_backend not in {"memory", "redis"}:
            raise ValueError("RATE_LIMIT_BACKEND must be memory or redis")

        if self.production_like:
            problems: list[str] = []
            if len(self.jwt_secret) < 32 or self.jwt_secret == "development-only-change-me":
                problems.append("JWT_SECRET must be a strong production secret")
            if len(self.admin_api_key) < 32:
                problems.append("ADMIN_API_KEY must be at least 32 characters")
            if len(self.admin_jwt_secret) < 32:
                problems.append("ADMIN_JWT_SECRET must be at least 32 characters")
            if self.admin_jwt_secret == self.jwt_secret:
                problems.append("ADMIN_JWT_SECRET must differ from JWT_SECRET")
            if not self.cookie_secure:
                problems.append("COOKIE_SECURE must be true")
            if self.creator_access_enabled:
                problems.append("CREATOR_ACCESS_ENABLED must be false")
            if self.sandbox_monetization_enabled:
                problems.append("SANDBOX_MONETIZATION_ENABLED must be false")
            if self.sandbox_rewarded_ads_enabled:
                problems.append("SANDBOX_REWARDED_ADS_ENABLED must be false")
            if not self.rate_limit_enabled:
                problems.append("RATE_LIMIT_ENABLED must be true")
            if self.rate_limit_backend != "redis":
                problems.append("RATE_LIMIT_BACKEND must be redis")
            if not self.push_token_encryption_key:
                problems.append("PUSH_TOKEN_ENCRYPTION_KEY is required")
            if problems:
                raise ValueError("; ".join(problems))
        return self


settings = Settings()
