import os
import warnings
from functools import lru_cache

from pydantic_settings import BaseSettings

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_default_db_path = os.path.join(_backend_dir, "platform.db")


class Settings(BaseSettings):
    # Environment: "development" or "production"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_default_db_path}"
    DATABASE_URL_SYNC: str = f"sqlite:///{_default_db_path}"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Paths
    MOCK_SOURCES_PATH: str = os.path.join(os.path.dirname(_backend_dir), "mock-sources")

    # External APIs
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.SECRET_KEY == "dev-secret-key-change-in-production":
        raise RuntimeError(
            "SECRET_KEY must be set to a secure random value in production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    if not settings.is_production and settings.SECRET_KEY == "dev-secret-key-change-in-production":
        warnings.warn("Using default SECRET_KEY — not safe for production", stacklevel=2)
    return settings
