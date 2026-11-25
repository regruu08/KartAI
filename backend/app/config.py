"""Centralized Application Configuration.

Enforces ADR-001 (configurable Gemini model), ADR-002 (configurable gateway fee),
and ADR-008 (strict CORS origin parsing).
All secrets must be wrapped in SecretStr. No os.getenv() calls outside this module!
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Final
from urllib.parse import urlencode

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

BACKEND_DIR: Final[Path] = Path(__file__).resolve().parent.parent
REPO_ROOT_DIR: Final[Path] = BACKEND_DIR.parent


def resolve_database_url(database_url: str, base_dir: Path = BACKEND_DIR) -> str:
    """Resolve relative SQLite paths deterministically against backend/ directory.

    Ensures launching uvicorn from repo root or backend/ always points to the
    single canonical backend/returnzero.db file while leaving in-memory, absolute
    file paths, and PostgreSQL URLs untouched.
    """
    raw = database_url.strip()
    try:
        parsed = make_url(raw)
    except ArgumentError:
        return raw

    if parsed.get_backend_name() != "sqlite":
        return raw

    db_path = parsed.database
    if not db_path or db_path == ":memory:" or db_path.startswith("file:"):
        return raw

    if Path(db_path).is_absolute() or db_path.startswith("/"):
        return raw

    resolved_path = (base_dir / db_path).resolve()
    query_suffix = f"?{urlencode(parsed.query, doseq=True)}" if parsed.query else ""
    return f"{parsed.drivername}:///{resolved_path.as_posix()}{query_suffix}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(REPO_ROOT_DIR / ".env"), str(BACKEND_DIR / ".env")),
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
    CORS_ORIGIN_REGEX: str = Field(
        default=r"^https://returnzero.*\.vercel\.app$",
        description="Optional regex pattern for allowed preview origins (e.g. Vercel previews)",
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
        gt=0.0,
        description="Hard timeout in seconds for Gemini API calls",
    )
    EXTRACT_RATE_LIMIT_PER_MIN: int = Field(
        default=30,
        ge=1,
        description="Maximum /extract requests per minute per client IP",
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
        ge=0.0,
        le=10.0,
        description="Payment gateway fee percentage for UPI (default 0.0 per pitch deck)",
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Resolve relative SQLite file paths deterministically."""
        return resolve_database_url(value)

    @property
    def cors_origins_list(self) -> list[str]:
        """Parsed list of allowed explicit CORS origins (never wildcard '*')."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip() and origin.strip() != "*"
        ]

    @property
    def cors_origin_regex(self) -> str | None:
        """Configured CORS origin regex or None if blank."""
        stripped = self.CORS_ORIGIN_REGEX.strip()
        return stripped or None

    @property
    def has_gemini_key(self) -> bool:
        """Check whether any Gemini API key is configured without exposing secrets."""
        return bool(self.PRIMARY_GEMINI_API_KEY or self.BACKUP_GEMINI_API_KEY)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
