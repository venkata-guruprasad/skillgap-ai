"""Health-check API routes."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.services.health_service import get_api_health, get_database_health

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check backend service health",
)
def health_check() -> HealthResponse:
    """Return service availability status."""
    return get_api_health()


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Check PostgreSQL database connectivity",
)
def database_health_check() -> JSONResponse:
    """Verify live PostgreSQL database connectivity."""
    result = get_database_health()
    http_status = (
        status.HTTP_200_OK
        if result.status == "success"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=http_status, content=result.model_dump())
