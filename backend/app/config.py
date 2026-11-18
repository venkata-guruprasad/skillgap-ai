"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env files from backend/ and project root (skillgap-ai/)
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

INSECURE_SECRET_MARKERS = (
    "replace_with",
    "dev-only",
    "changeme",
    "secret_key",
    "example",
)


def normalize_database_url(raw_url: str) -> str:
    """Normalize managed PostgreSQL URLs (Neon, Supabase, Render, Railway) for SQLAlchemy 2."""
    cleaned = raw_url.strip()
    if cleaned.startswith("postgres://"):
        return "postgresql+psycopg2://" + cleaned[len("postgres://") :]
    if cleaned.startswith("postgresql://"):
        return "postgresql+psycopg2://" + cleaned[len("postgresql://") :]
    return cleaned


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application metadata
    APP_NAME: str = "SkillGap AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # "development" | "staging" | "production"
    DEBUG: bool = True
    ENABLE_API_DOCS: bool = True
    API_V1_PREFIX: str = "/api"

    # Optional Configurable LLM Integration (Phase 7; never expose keys)
    LLM_PROVIDER: str = "none"  # "none" | "openai" | "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    LLM_BASE_URL: str = ""
    LLM_TIMEOUT_SECONDS: int = 25

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # PostgreSQL configuration (provided via environment variables; never hardcoded)
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Local SQLite development fallback (used ONLY in development when PostgreSQL env vars are unset)
    ENABLE_LOCAL_SQLITE_FALLBACK: bool = True
    LOCAL_SQLITE_PATH: str = str(BACKEND_DIR / "skillgap_dev.db")

    # Security / JWT Auth
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Resume Upload Settings
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB strict limit
    UPLOAD_DIR: str = str(PROJECT_ROOT / "data" / "uploads")

    @field_validator("POSTGRES_PORT", mode="before")
    @classmethod
    def parse_port(cls, value: object) -> int:
        if value in (None, ""):
            return 5432
        return int(value)

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.strip().lower() not in {"development", "dev", "test"}

    @property
    def effective_debug(self) -> bool:
        """Never allow debug mode in non-development environments."""
        if self.is_production:
            return False
        return bool(self.DEBUG)

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a clean list (strip trailing slashes)."""
        return [
            origin.strip().rstrip("/")
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def effective_secret_key(self) -> str:
        """Return validated SECRET_KEY, or an explicit dev-only fallback in development."""
        secret = (self.SECRET_KEY or "").strip()
        if not self.is_production:
            return secret or "skillgap-dev-only-jwt-secret-change-in-production"

        lowered = secret.lower()
        if len(secret) < 32 or any(marker in lowered for marker in INSECURE_SECRET_MARKERS):
            raise RuntimeError(
                "Production SECRET_KEY must be a random string of at least 32 characters "
                "and must not use placeholder values."
            )
        return secret

    @property
    def effective_database_url(self) -> Optional[str]:
        """Return PostgreSQL DATABASE_URL, or local SQLite fallback ONLY in development."""
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            return normalize_database_url(self.DATABASE_URL)

        if self.POSTGRES_HOST and self.POSTGRES_USER and self.POSTGRES_DB:
            user = quote_plus(self.POSTGRES_USER)
            password = quote_plus(self.POSTGRES_PASSWORD)
            auth = f"{user}:{password}" if self.POSTGRES_PASSWORD else user
            return (
                f"postgresql+psycopg2://{auth}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if not self.is_production and self.ENABLE_LOCAL_SQLITE_FALLBACK:
            sqlite_path = Path(self.LOCAL_SQLITE_PATH).resolve().as_posix()
            return f"sqlite:///{sqlite_path}"

        return None

    @property
    def is_postgres_configured(self) -> bool:
        """True when an explicit PostgreSQL connection is configured."""
        url = self.effective_database_url or ""
        return url.startswith("postgresql")

    def validate_production_config(self) -> None:
        """Fail fast at startup if production security/database requirements are violated."""
        if not self.is_production:
            return

        # 1. Validate strong JWT secret
        _ = self.effective_secret_key

        # 2. Require PostgreSQL in production (never SQLite)
        if not self.is_postgres_configured:
            raise RuntimeError(
                "PostgreSQL must be configured in production via DATABASE_URL or POSTGRES_* vars."
            )

        # 3. Forbid wildcard CORS with credentials enabled
        origins = self.cors_origins_list
        if not origins or "*" in origins:
            raise RuntimeError(
                "CORS_ORIGINS must specify explicit frontend domain(s) in production (no '*')."
            )


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()


settings = get_settings()
