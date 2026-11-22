from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./study_tracker.db"
    secret_key: str = "study-tracker-super-secret-key-change-in-production-12345"
    algorithm: str = "HS256"
    token_minutes: int = 60
    cors_origins: list[str] = ["*"]
    app_title: str = "Study Tracker API"
    app_version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
