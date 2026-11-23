"""Centralized Application Configuration.

Enforces ADR-001 (configurable Gemini model), ADR-002 (configurable gateway fee),
and ADR-008 (strict CORS origin parsing).
All secrets must be wrapped in SecretStr. No os.getenv() calls outside this module!
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service & Environment
    SERVICE_NAME: str = Field(default="returnzero-api", description="Service identifier")
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    PORT: int = Field(default=8000, description="Bind port")

    # CORS Settings (ADR-008: comma-separated list of fully-qualified domains)
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated allowed CORS origins",
    )

    # Database Settings (ADR-019: async SQLite default with PostgreSQL compatibility)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./returnzero.db",
        description="SQLAlchemy 2.0 database URL",
    )

    # Gemini VLM Settings (ADR-001 & ADR-016)
    GEMINI_MODEL_ID: str = Field(
        default="gemini-3.8-flash",
        description="Target Gemini model identifier",
    )
    PRIMARY_GEMINI_API_KEY: SecretStr | None = Field(
        default=None,
        description="Primary Google GenAI API key",
    )
    BACKUP_GEMINI_API_KEY: SecretStr | None = Field(
        default=None,
        description="Secondary fallback Google GenAI API key",
    )
    GEMINI_TIMEOUT_S: float = Field(
        default=4.0,
        description="Hard timeout in seconds for Gemini API calls",
    )

    # Demo & Admin Settings (ADR-009)
    DEMO_MODE: bool = Field(
        default=True,
        description="Enable demo reset endpoint and seeded states",
    )
    DEMO_TOKEN: SecretStr = Field(
        default=SecretStr("returnzero-demo-secret-2026"),
        description="Guarded token for /v1/demo/reset endpoint",
    )

    # Financial / Incentive Solver Settings (ADR-002)
    UPI_GATEWAY_FEE_PCT: float = Field(
        default=0.0,
        description="Payment gateway fee percentage for UPI (default 0.0 per pitch deck)",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parsed list of allowed CORS origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def has_gemini_key(self) -> bool:
        """Check whether any Gemini API key is configured without exposing secrets."""
        return bool(self.PRIMARY_GEMINI_API_KEY or self.BACKUP_GEMINI_API_KEY)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
