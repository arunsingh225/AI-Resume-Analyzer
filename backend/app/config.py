"""
Centralized configuration using Pydantic Settings.
All secrets and tunables are loaded from environment / .env file.
"""
import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Auth ──
    jwt_secret: str = "CHANGE_IN_PRODUCTION_REQUIRED"
    jwt_algorithm: str = "HS256"

    # ── Database ──
    database_url: str = "sqlite:///./resume_analyzer.db"

    # ── Upload ──
    max_upload_mb: int = 10

    # ── CORS (stored as comma-separated string for env var compatibility) ──
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [s.strip() for s in self.cors_origins.split(",") if s.strip()]

    # ── AI Feature Flags ──
    enable_semantic_matching: bool = True
    enable_llm_rewrite: bool = False
    openai_api_key: str = ""

    # ── Google OAuth ──
    google_client_id: str = ""

    # ── Rate Limiting ──
    rate_limit_auth: str = "5/minute"
    rate_limit_analyze: str = "10/minute"

    # ── Logging ──
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — reads .env only once per process."""
    return Settings()
