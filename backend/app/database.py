"""SQLAlchemy database engine, session factory, and connectivity utilities."""

import logging
from typing import Generator, Optional, Tuple

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger("skillgap_ai.database")


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""


def create_db_engine(database_url: Optional[str] = None) -> Optional[Engine]:
    """Create a SQLAlchemy engine for PostgreSQL or local SQLite dev fallback."""
    url = database_url or settings.effective_database_url
    if not url:
        return None

    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        echo=False,
    )


engine: Optional[Engine] = create_db_engine()

SessionLocal: Optional[sessionmaker[Session]] = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if engine is not None
    else None
)


def init_db() -> None:
    """Create tables automatically when running against the local SQLite dev fallback."""
    if engine is None:
        return
    import app.models  # noqa: F401 - register all ORM models on Base.metadata

    if engine.dialect.name == "sqlite":
        Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a scoped SQLAlchemy session."""
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL or POSTGRES_* environment variables."
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Tuple[bool, str]:
    """Verify live connectivity to the configured database by running SELECT 1."""
    if engine is None:
        return (
            False,
            "Database URL is not configured. Set POSTGRES_HOST, POSTGRES_USER, "
            "POSTGRES_PASSWORD, and POSTGRES_DB (or DATABASE_URL) in .env.",
        )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        if engine.dialect.name == "postgresql":
            return True, "PostgreSQL connection successful"
        return (
            True,
            f"Connected via {engine.dialect.name} (local dev fallback; configure POSTGRES_* for PostgreSQL)",
        )
    except SQLAlchemyError as exc:
        logger.error("Database health check failed: %s", exc.__class__.__name__)
        if settings.is_production:
            return False, "PostgreSQL connection unavailable."
        return False, f"Database connection failed: {exc.__class__.__name__}"
