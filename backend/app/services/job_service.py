"""Job Description Analyzer service: creation, retrieval, listing, and sample job seeding."""

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.ml.jd_analyzer import analyze_job_description
from app.ml.sample_jobs import SAMPLE_JOB_DESCRIPTIONS
from app.models.analysis import JobDescription
from app.models.user import User
from app.schemas.analysis import (
    JobCreateRequest,
    JobDetailResponse,
    JobExtractedPayload,
    JobListItem,
    JobListResponse,
)

logger = logging.getLogger("skillgap_ai.job_service")


def _to_job_detail(row: JobDescription) -> JobDetailResponse:
    extracted = JobExtractedPayload.model_validate(row.extracted_skills or {})
    return JobDetailResponse(
        id=row.id,
        title=row.title,
        company=row.company,
        category=row.category,
        location=row.location,
        work_mode=row.work_mode,
        experience_level=row.experience_level,
        salary_range=row.salary_range,
        is_sample=bool(row.is_sample),
        raw_text=row.raw_text,
        extracted=extracted,
        created_at=row.created_at,
    )


def seed_sample_jobs(db: Session) -> int:
    """Idempotently seed all 8 clearly labeled sample job descriptions."""
    inserted = 0
    for sample in SAMPLE_JOB_DESCRIPTIONS:
        exists = (
            db.query(JobDescription)
            .filter(
                JobDescription.is_sample.is_(True),
                JobDescription.title == sample["title"],
            )
            .first()
        )
        if exists is not None:
            continue

        extracted = analyze_job_description(sample["raw_text"])
        db.add(
            JobDescription(
                user_id=None,
                title=sample["title"],
                company=sample["company"],
                category=sample["category"],
                location=sample.get("location"),
                work_mode=sample.get("work_mode"),
                experience_level=sample.get("experience_level"),
                salary_range=sample.get("salary_range"),
                is_sample=True,
                raw_text=sample["raw_text"].strip(),
                extracted_skills=extracted,
            )
        )
        inserted += 1

    if inserted > 0:
        db.commit()
        logger.info("Seeded %d sample job descriptions.", inserted)
    return inserted


def create_job_description(
    payload: JobCreateRequest,
    current_user: User,
    db: Session,
) -> JobDetailResponse:
    """Validate, analyze, and persist a user-submitted job description."""
    raw_text = payload.raw_text.strip()
    if sum(1 for ch in raw_text if ch.isalnum()) < 25:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Job description must contain meaningful text (at least 25 alphanumeric characters).",
        )

    extracted = analyze_job_description(raw_text)
    if (
        len(extracted.get("required_skills", [])) == 0
        and len(extracted.get("preferred_skills", [])) == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "No recognizable technical skills were detected in this job description. "
                "Please include role requirements and technical qualifications."
            ),
        )

    job = JobDescription(
        user_id=current_user.id,
        title=payload.title.strip(),
        company=payload.company.strip(),
        category=payload.category.strip(),
        location=payload.location.strip() if payload.location else None,
        work_mode=payload.work_mode.strip() if payload.work_mode else None,
        experience_level=payload.experience_level.strip() if payload.experience_level else None,
        salary_range=payload.salary_range.strip() if payload.salary_range else None,
        is_sample=False,
        raw_text=raw_text,
        extracted_skills=extracted,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _to_job_detail(job)


def list_jobs(
    db: Session,
    current_user: Optional[User] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> JobListResponse:
    """List seeded sample jobs plus the authenticated user's custom job descriptions."""
    query = db.query(JobDescription)
    if current_user is not None:
        query = query.filter(
            or_(
                JobDescription.is_sample.is_(True),
                JobDescription.user_id == current_user.id,
            )
        )
    else:
        query = query.filter(JobDescription.is_sample.is_(True))

    if category and category.lower() != "all":
        query = query.filter(JobDescription.category == category)

    rows = query.order_by(JobDescription.is_sample.asc(), JobDescription.created_at.desc()).all()

    search_q = (search or "").strip().lower()
    items = []
    for row in rows:
        extracted = row.extracted_skills or {}
        req_skills = extracted.get("required_skills", [])
        pref_skills = extracted.get("preferred_skills", [])

        if search_q:
            hay = " ".join(
                [
                    row.title or "",
                    row.company or "",
                    row.category or "",
                    row.location or "",
                    *(s.get("name", "") for s in req_skills),
                    *(s.get("name", "") for s in pref_skills),
                ]
            ).lower()
            if search_q not in hay:
                continue

        items.append(
            JobListItem(
                id=row.id,
                title=row.title,
                company=row.company,
                category=row.category,
                location=row.location,
                work_mode=row.work_mode,
                experience_level=row.experience_level,
                salary_range=row.salary_range,
                is_sample=bool(row.is_sample),
                required_skills=req_skills,
                preferred_skills=pref_skills,
                required_skill_count=len(req_skills),
                preferred_skill_count=len(pref_skills),
                created_at=row.created_at,
            )
        )

    return JobListResponse(total=len(items), items=items)


def get_job_by_id(
    job_id: int,
    db: Session,
    current_user: Optional[User] = None,
) -> JobDetailResponse:
    """Retrieve a single job description (sample jobs or owner's custom jobs)."""
    row = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    if not row.is_sample and (current_user is None or row.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    return _to_job_detail(row)
