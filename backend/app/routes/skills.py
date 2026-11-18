"""Standalone NLP skill extraction API routes."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import SkillExtractRequest, SkillExtractResponse
from app.services.resume_service import extract_skills_from_raw_text

router = APIRouter(prefix="/skills", tags=["Skill Extraction"])


@router.post(
    "/extract",
    response_model=SkillExtractResponse,
    summary="Extract normalized technical & soft skills with evidence snippets from text",
)
def extract_skills(
    payload: SkillExtractRequest,
    current_user: User = Depends(get_current_user),
) -> SkillExtractResponse:
    _ = current_user  # enforce authentication
    return extract_skills_from_raw_text(payload.text)
