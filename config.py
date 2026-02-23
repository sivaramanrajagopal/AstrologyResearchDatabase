"""
Application config using Pydantic Settings.
Load from environment and .env; validate required settings.
"""
import os
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore

from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings from environment."""

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_KEY: str = ""  # alias for anon key if used
    EPHE_PATH: str = "ephe"
    REDIS_URL: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DEBUG: bool = False
    API_VERSION: str = "v1"
    CORS_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    CACHE_TTL: int = 3600
    MAX_BATCH_SIZE: int = 10
    CAREER_API_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @field_validator("SUPABASE_URL", mode="before")
    @classmethod
    def validate_supabase_url(cls, v: str) -> str:
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("SUPABASE_URL must be a valid URL")
        return (v or "").strip()

    @field_validator("REDIS_PORT")
    @classmethod
    def validate_redis_port(cls, v: int) -> int:
        if v < 1 or v > 65535:
            raise ValueError("REDIS_PORT must be 1-65535")
        return v

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and (self.SUPABASE_ANON_KEY or self.SUPABASE_KEY))

    @property
    def ephe_path_exists(self) -> bool:
        return Path(self.EPHE_PATH).exists()


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
