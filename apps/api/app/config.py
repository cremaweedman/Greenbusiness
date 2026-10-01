from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://greenbusiness:change-me@postgres:5432/greenbusiness"

    jwt_secret: str = "development-only-change-me"
    jwt_issuer: str = "greenbusiness"
    jwt_access_ttl_seconds: int = 900
    refresh_ttl_seconds: int = 2_592_000
    refresh_cookie_name: str = "gb_refresh"
    cookie_secure: bool = False
    admin_api_key: str = "development-admin-change-me"
    creator_access_enabled: bool = True
    creator_email: str = "creator@greenbusiness.local"
    creator_display_name: str = "Creator"

    storage_backend: str = "local"
    storage_local_path: str = "/data/greenbusiness"
    s3_endpoint: str | None = None
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
