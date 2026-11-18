"""Job Description API routes: list, create, and retrieve."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analysis import (
    JobCreateRequest,
    JobDetailResponse,
    JobListResponse,
)
from app.services.job_service import (
    create_job_description,
    get_job_by_id,
    list_jobs,
)
from app.utils.security import decode_access_token

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])
optional_bearer = HTTPBearer(auto_error=False)


def _get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub", 0))
    except (jwt.PyJWTError, ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()


@router.get(
    "",
    response_model=JobListResponse,
    summary="List seeded sample job descriptions and user's saved job descriptions",
)
def get_jobs(
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    current_user: Optional[User] = Depends(_get_optional_user),
    db: Session = Depends(get_db),
) -> JobListResponse:
    return list_jobs(db=db, current_user=current_user, category=category, search=search)


@router.post(
    "",
    response_model=JobDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze and store a custom job description",
)
def post_job(
    payload: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetailResponse:
    return create_job_description(payload=payload, current_user=current_user, db=db)


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Retrieve full extracted details for a job description",
)
def get_job(
    job_id: int,
    current_user: Optional[User] = Depends(_get_optional_user),
    db: Session = Depends(get_db),
) -> JobDetailResponse:
    return get_job_by_id(job_id=job_id, db=db, current_user=current_user)
