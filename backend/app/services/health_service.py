"""Business logic layer for application and database health checks."""

from app.database import check_db_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse


def get_api_health() -> HealthResponse:
    """Return the standard API health response."""
    return HealthResponse(
        status="success",
        message="SkillGap AI backend is running",
    )


def get_database_health() -> DatabaseHealthResponse:
    """Verify PostgreSQL connectivity and return structured status."""
    is_connected, detail = check_db_connection()
    return DatabaseHealthResponse(
        status="success" if is_connected else "error",
        database="connected" if is_connected else "disconnected",
        message=detail,
    )
