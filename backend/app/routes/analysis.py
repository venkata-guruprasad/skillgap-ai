"""Skill Gap Analysis API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analysis import (
    SkillGapDetailResponse,
    SkillGapHistoryResponse,
    SkillGapRequest,
)
from app.services.analysis_service import (
    get_analysis_by_id,
    list_analysis_history,
    run_and_store_skill_gap_analysis,
)

router = APIRouter(prefix="/analysis", tags=["Skill Gap Engine"])


@router.post(
    "/skill-gap",
    response_model=SkillGapDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run explainable weighted skill gap analysis with semantic matching",
)
def create_skill_gap(
    payload: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillGapDetailResponse:
    return run_and_store_skill_gap_analysis(
        payload=payload, current_user=current_user, db=db
    )


@router.get(
    "/history",
    response_model=SkillGapHistoryResponse,
    summary="List persisted skill gap analysis history for the authenticated user",
)
def get_skill_gap_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillGapHistoryResponse:
    return list_analysis_history(current_user=current_user, db=db)


@router.get(
    "/{analysis_id}",
    response_model=SkillGapDetailResponse,
    summary="Retrieve a specific persisted skill gap analysis",
)
def get_skill_gap_detail(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillGapDetailResponse:
    return get_analysis_by_id(
        analysis_id=analysis_id, current_user=current_user, db=db
    )
