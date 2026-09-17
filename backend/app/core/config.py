"""
Application configuration.

All runtime configuration is read from environment variables (loaded from a
local .env file when present). This is the single source of truth for
settings such as which AI provider to use and where the database lives.

Keeping configuration in one Pydantic Settings object (instead of scattering
os.environ.get(...) calls across the codebase) makes it obvious what the
app depends on and gives us validation "for free" (e.g. wrong types fail
fast at startup instead of causing a confusing bug later).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "AI Technician Request Classifier"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- AI provider selection ---
    # "mock"   -> deterministic, rule-based fake AI. No API key required.
    # "gemini" -> Google Gemini API.
    # "openai" -> OpenAI API.
    AI_PROVIDER: str = "mock"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Timeout (seconds) for outbound calls to the LLM provider.
    AI_REQUEST_TIMEOUT_SECONDS: float = 20.0

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # --- CORS ---
    # Comma-separated list of allowed origins for the frontend during
    # development. Deliberately NOT "*" - see README "Security Considerations".
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Validation limits ---
    # Applied server-side, regardless of whatever the frontend enforces.
    MIN_DESCRIPTION_LENGTH: int = 3
    MAX_DESCRIPTION_LENGTH: int = 2000
    MIN_PROBLEM_LENGTH: int = 2
    MAX_PROBLEM_LENGTH: int = 500

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse the environment only once."""
    return Settings()
