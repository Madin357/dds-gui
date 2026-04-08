from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://dds:dds_dev_password@localhost:5432/dds_platform"
    DATABASE_URL_SYNC: str = "postgresql://dds:dds_dev_password@localhost:5432/dds_platform"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MOCK_SOURCES_PATH: str = "../mock-sources"
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
