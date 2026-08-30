from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "CREST API"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_BASE_URL: str = "http://localhost:8000"

    # Stored as a comma-separated string so pydantic-settings doesn't try to
    # JSON-decode it from the environment. Use the `frontend_origins` property
    # to consume it as a list.
    FRONTEND_ORIGINS: str = ""

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "crest"
    DB_PASSWORD: str = ""
    DB_NAME: str = "crest"

    SECRET_KEY: str = "insecure-dev-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    RATE_LIMIT_DEFAULT: str = "120/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_CONTACT: str = "5/minute"

    COOKIE_SECURE: bool = False

    @property
    def frontend_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.FRONTEND_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def database_url(self) -> str:
        # Allow explicit override (useful for SQLite in dev or for testing).
        import os
        override = os.getenv("DATABASE_URL")
        if override:
            return override
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
