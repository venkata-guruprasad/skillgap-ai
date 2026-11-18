"""Personalized AI Learning Roadmap API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapDetailResponse,
    RoadmapGenerateRequest,
    RoadmapListResponse,
    RoadmapTaskUpdateRequest,
    RoadmapTaskUpdateResponse,
)
from app.services.roadmap_service import (
    create_generated_roadmap,
    get_user_roadmap_by_id,
    list_user_roadmaps,
    update_user_roadmap_task,
)

router = APIRouter(prefix="/roadmap", tags=["AI Learning Roadmap"])


@router.post(
    "/generate",
    response_model=RoadmapDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and persist a personalized 30, 60, or 90-day learning roadmap",
)
def generate_roadmap(
    payload: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoadmapDetailResponse:
    return create_generated_roadmap(payload=payload, current_user=current_user, db=db)


@router.get(
    "",
    response_model=RoadmapListResponse,
    summary="List all learning roadmaps (history & progress) for the authenticated user",
)
def get_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoadmapListResponse:
    return list_user_roadmaps(current_user=current_user, db=db)


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapDetailResponse,
    summary="Retrieve full phases, resources, and task states for a learning roadmap",
)
def get_roadmap_detail(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoadmapDetailResponse:
    return get_user_roadmap_by_id(
        roadmap_id=roadmap_id, current_user=current_user, db=db
    )


@router.patch(
    "/tasks/{task_id}",
    response_model=RoadmapTaskUpdateResponse,
    summary="Mark a roadmap learning task complete or incomplete with DB persistence",
)
def patch_roadmap_task(
    task_id: int,
    payload: RoadmapTaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoadmapTaskUpdateResponse:
    return update_user_roadmap_task(
        task_id=task_id,
        is_completed=payload.is_completed,
        current_user=current_user,
        db=db,
    )
