from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://greenbusiness:change-me@postgres:5432/greenbusiness"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
