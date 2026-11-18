"""Skill Gap Analysis service: orchestrates semantic matching, weighted scoring, and history."""

from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.skill_gap_engine import run_skill_gap_engine
from app.models.analysis import JobDescription, SkillGapAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import (
    JobExtractedPayload,
    SkillGapDetailResponse,
    SkillGapHistoryItem,
    SkillGapHistoryResponse,
    SkillGapRequest,
)
from app.services.job_service import create_job_description


def _resolve_candidate_skills(
    payload: SkillGapRequest,
    current_user: User,
    db: Session,
) -> Tuple[List[str], Optional[Resume]]:
    """Resolve verified candidate skills from an owned Resume record or explicit candidate_skills list."""
    resume_row: Optional[Resume] = None

    if payload.resume_id is not None:
        resume_row = (
            db.query(Resume)
            .filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id)
            .first()
        )
        if resume_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected resume was not found in your account.",
            )

    if payload.candidate_skills is not None and len(payload.candidate_skills) > 0:
        skills = [s.strip() for s in payload.candidate_skills if s and s.strip()]
        if skills:
            return skills, resume_row

    if resume_row is None:
        # Automatically fall back to the user's most recently analyzed resume if available
        resume_row = (
            db.query(Resume)
            .filter(Resume.user_id == current_user.id)
            .order_by(Resume.created_at.desc(), Resume.id.desc())
            .first()
        )

    if resume_row is not None:
        parsed = resume_row.parsed_data or {}
        tech_skills = [
            item["name"]
            for item in parsed.get("technical_skills", [])
            if isinstance(item, dict) and item.get("name")
        ]
        if tech_skills:
            return tech_skills, resume_row

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=(
            "No candidate skills available for analysis. Upload a resume first or "
            "provide candidate_skills in the request."
        ),
    )


def _resolve_job_record(
    payload: SkillGapRequest,
    current_user: User,
    db: Session,
) -> JobDescription:
    if payload.custom_job is not None:
        created = create_job_description(payload.custom_job, current_user, db)
        row = db.query(JobDescription).filter(JobDescription.id == created.id).first()
        if row is None:
            raise HTTPException(status_code=500, detail="Failed to reload created job.")
        return row

    if payload.job_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Provide either job_id or custom_job to run a skill gap analysis.",
        )

    row = db.query(JobDescription).filter(JobDescription.id == payload.job_id).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target job description not found.",
        )

    if not row.is_sample and row.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target job description not found.",
        )

    return row


def run_and_store_skill_gap_analysis(
    payload: SkillGapRequest,
    current_user: User,
    db: Session,
) -> SkillGapDetailResponse:
    """Run the semantic + exact weighted skill gap engine and persist the analysis record."""
    candidate_skills, resume_row = _resolve_candidate_skills(payload, current_user, db)
    job_row = _resolve_job_record(payload, current_user, db)

    extracted = job_row.extracted_skills or {}
    required_skills = extracted.get("required_skills", [])
    preferred_skills = extracted.get("preferred_skills", [])

    if not required_skills and preferred_skills:
        # Promote preferred skills if a minimal JD only listed preferred items
        required_skills = preferred_skills
        preferred_skills = []

    if not required_skills:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Selected job description has no extracted required skills to compare.",
        )

    result = run_skill_gap_engine(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        resume_text=resume_row.raw_text if resume_row else None,
        jd_text=job_row.raw_text,
    )

    analysis_row = SkillGapAnalysis(
        user_id=current_user.id,
        resume_id=resume_row.id if resume_row else None,
        job_description_id=job_row.id,
        match_score=Decimal(str(result["compatibility_score"])),
        matched_skills=result["matched_required_skills"],
        missing_skills=result["missing_required_skills"],
        recommendations={
            "preferred_score": result["preferred_score"],
            "jd_semantic_similarity": result["jd_semantic_similarity"],
            "matched_preferred_skills": result["matched_preferred_skills"],
            "missing_preferred_skills": result["missing_preferred_skills"],
            "additional_skills": result["additional_skills"],
            "category_breakdown": result["category_breakdown"],
            "radar_data": result["radar_data"],
            "score_explanation": result["score_explanation"],
            "candidate_skills_used": candidate_skills,
        },
    )
    db.add(analysis_row)
    db.commit()
    db.refresh(analysis_row)

    return SkillGapDetailResponse(
        id=analysis_row.id,
        resume_id=resume_row.id if resume_row else None,
        resume_file_name=resume_row.file_name if resume_row else None,
        job_id=job_row.id,
        job_title=job_row.title,
        job_company=job_row.company,
        job_category=job_row.category,
        is_sample_job=bool(job_row.is_sample),
        compatibility_score=result["compatibility_score"],
        preferred_score=result["preferred_score"],
        jd_semantic_similarity=result["jd_semantic_similarity"],
        matched_required_skills=result["matched_required_skills"],
        missing_required_skills=result["missing_required_skills"],
        matched_preferred_skills=result["matched_preferred_skills"],
        missing_preferred_skills=result["missing_preferred_skills"],
        additional_skills=result["additional_skills"],
        category_breakdown=result["category_breakdown"],
        radar_data=result["radar_data"],
        score_explanation=result["score_explanation"],
        job_details=JobExtractedPayload.model_validate(extracted),
        created_at=analysis_row.created_at,
    )


def list_analysis_history(
    current_user: User,
    db: Session,
) -> SkillGapHistoryResponse:
    """List persisted skill gap analyses for the authenticated user (most recent first)."""
    rows = (
        db.query(SkillGapAnalysis)
        .filter(SkillGapAnalysis.user_id == current_user.id)
        .order_by(SkillGapAnalysis.created_at.desc(), SkillGapAnalysis.id.desc())
        .limit(50)
        .all()
    )

    items: List[SkillGapHistoryItem] = []
    for row in rows:
        job = (
            db.query(JobDescription)
            .filter(JobDescription.id == row.job_description_id)
            .first()
            if row.job_description_id
            else None
        )
        resume = (
            db.query(Resume).filter(Resume.id == row.resume_id).first()
            if row.resume_id
            else None
        )
        extra = row.recommendations or {}
        items.append(
            SkillGapHistoryItem(
                id=row.id,
                resume_id=row.resume_id,
                resume_file_name=resume.file_name if resume else None,
                job_id=row.job_description_id,
                job_title=job.title if job else "Deleted Job",
                job_company=job.company if job else None,
                job_category=job.category if job else "General",
                is_sample_job=bool(job.is_sample) if job else False,
                compatibility_score=float(row.match_score or 0.0),
                preferred_score=extra.get("preferred_score"),
                jd_semantic_similarity=float(extra.get("jd_semantic_similarity") or 0.0),
                matched_required_count=len(row.matched_skills or []),
                missing_required_count=len(row.missing_skills or []),
                additional_skill_count=len(extra.get("additional_skills") or []),
                created_at=row.created_at,
            )
        )

    return SkillGapHistoryResponse(total=len(items), items=items)


def get_analysis_by_id(
    analysis_id: int,
    current_user: User,
    db: Session,
) -> SkillGapDetailResponse:
    """Retrieve a specific persisted skill gap analysis owned by the user."""
    row = (
        db.query(SkillGapAnalysis)
        .filter(
            SkillGapAnalysis.id == analysis_id,
            SkillGapAnalysis.user_id == current_user.id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill gap analysis not found.",
        )

    job = (
        db.query(JobDescription)
        .filter(JobDescription.id == row.job_description_id)
        .first()
    )
    resume = (
        db.query(Resume).filter(Resume.id == row.resume_id).first()
        if row.resume_id
        else None
    )
    extra = row.recommendations or {}

    return SkillGapDetailResponse(
        id=row.id,
        resume_id=row.resume_id,
        resume_file_name=resume.file_name if resume else None,
        job_id=job.id if job else 0,
        job_title=job.title if job else "Unknown Job",
        job_company=job.company if job else None,
        job_category=job.category if job else "General",
        is_sample_job=bool(job.is_sample) if job else False,
        compatibility_score=float(row.match_score or 0.0),
        preferred_score=extra.get("preferred_score"),
        jd_semantic_similarity=float(extra.get("jd_semantic_similarity") or 0.0),
        matched_required_skills=row.matched_skills or [],
        missing_required_skills=row.missing_skills or [],
        matched_preferred_skills=extra.get("matched_preferred_skills") or [],
        missing_preferred_skills=extra.get("missing_preferred_skills") or [],
        additional_skills=extra.get("additional_skills") or [],
        category_breakdown=extra.get("category_breakdown") or [],
        radar_data=extra.get("radar_data") or [],
        score_explanation=extra.get("score_explanation"),
        job_details=JobExtractedPayload.model_validate(
            (job.extracted_skills if job else None) or {}
        ),
        created_at=row.created_at,
    )
