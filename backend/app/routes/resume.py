"""Resume upload, history, detail, and deletion API routes."""

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import (
    ResumeDeleteResponse,
    ResumeDetailResponse,
    ResumeHistoryResponse,
)
from app.services.resume_service import (
    delete_user_resume_by_id,
    get_user_resume_by_id,
    list_user_resumes,
    upload_and_analyze_resume,
)

router = APIRouter(prefix="/resume", tags=["Resume Analyzer"])


@router.post(
    "/upload",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze a PDF or DOCX resume (max 5 MB)",
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDetailResponse:
    return await upload_and_analyze_resume(file=file, current_user=current_user, db=db)


@router.get(
    "/history",
    response_model=ResumeHistoryResponse,
    summary="List uploaded resume history for the authenticated user",
)
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeHistoryResponse:
    return list_user_resumes(current_user=current_user, db=db)


@router.get(
    "/{resume_id}",
    response_model=ResumeDetailResponse,
    summary="Retrieve detailed NLP analysis for an uploaded resume",
)
def get_resume_detail(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDetailResponse:
    return get_user_resume_by_id(resume_id=resume_id, current_user=current_user, db=db)


@router.delete(
    "/{resume_id}",
    response_model=ResumeDeleteResponse,
    summary="Delete an uploaded resume and its stored file",
)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeDeleteResponse:
    return delete_user_resume_by_id(
        resume_id=resume_id, current_user=current_user, db=db
    )
