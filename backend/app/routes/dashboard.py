"""Dashboard analytics API route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardAnalyticsResponse
from app.services.dashboard_service import build_dashboard_analytics

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])


@router.get(
    "/analytics",
    response_model=DashboardAnalyticsResponse,
    summary="Return aggregated live dashboard analytics for the authenticated user",
)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardAnalyticsResponse:
    return build_dashboard_analytics(current_user=current_user, db=db)
