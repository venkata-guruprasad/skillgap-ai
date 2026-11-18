"""Career Prediction service: bridges user resume/profile inputs, ML recommender, and DB persistence."""

from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.career.career_recommender import EMPLOYMENT_DISCLAIMER, predict_top_careers
from app.models.analysis import JobDescription
from app.models.career_prediction import CareerPredictionRecord
from app.models.resume import Resume
from app.models.user import User
from app.schemas.career import CareerPredictionResponse, CareerPredictRequest


def _extract_profile_from_resume(
    resume: Resume,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    parsed = resume.parsed_data or {}
    skills = [
        item["name"]
        for item in parsed.get("technical_skills", [])
        if isinstance(item, dict) and item.get("name")
    ]
    education = [
        " - ".join(filter(None, [e.get("degree"), e.get("institution")]))
        for e in parsed.get("education", [])
        if isinstance(e, dict) and (e.get("degree") or e.get("institution"))
    ]
    experience = [
        " ".join(
            filter(
                None,
                [
                    e.get("role"),
                    e.get("organization"),
                    " ".join(e.get("highlights", [])[:2]),
                ],
            )
        )
        for e in parsed.get("experience", [])
        if isinstance(e, dict)
    ]
    projects = [
        " - ".join(filter(None, [p.get("title"), p.get("description")]))
        for p in parsed.get("projects", [])
        if isinstance(p, dict)
    ]
    return skills, education, experience, projects


def _build_job_title_lookup(db: Session, user_id: int) -> Dict[str, int]:
    rows = (
        db.query(JobDescription)
        .filter((JobDescription.is_sample.is_(True)) | (JobDescription.user_id == user_id))
        .all()
    )
    return {row.title: row.id for row in rows if row.title}


def run_career_prediction(
    payload: CareerPredictRequest,
    current_user: User,
    db: Session,
) -> CareerPredictionResponse:
    """Predict top 5 career roles using trained ML classifier, MiniLM cosine similarity, and Skill Gap Engine."""
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
    elif not payload.resume_skills:
        resume_row = (
            db.query(Resume)
            .filter(Resume.user_id == current_user.id)
            .order_by(Resume.created_at.desc(), Resume.id.desc())
            .first()
        )

    res_skills: List[str] = []
    res_edu: List[str] = []
    res_exp: List[str] = []
    res_proj: List[str] = []
    if resume_row is not None:
        res_skills, res_edu, res_exp, res_proj = _extract_profile_from_resume(resume_row)

    merged_skills = list(
        dict.fromkeys(
            [s.strip() for s in (payload.resume_skills or []) if s and s.strip()]
            or res_skills
        )
    )
    merged_edu = payload.education or res_edu
    merged_exp = payload.experience or res_exp
    merged_proj = payload.projects or res_proj
    interests = [i.strip() for i in payload.career_interests if i and i.strip()]

    if not merged_skills and not merged_edu and not merged_exp and not merged_proj:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Provide resume_skills, education/experience/projects, or upload a resume "
                "before requesting career predictions."
            ),
        )

    job_lookup = _build_job_title_lookup(db, current_user.id)
    result = predict_top_careers(
        resume_skills=merged_skills,
        education=merged_edu,
        experience=merged_exp,
        projects=merged_proj,
        career_interests=interests,
        top_k=5,
        job_title_to_id=job_lookup,
    )

    input_summary = {
        "skill_count": len(merged_skills),
        "skills_used": merged_skills,
        "education_count": len(merged_edu),
        "experience_count": len(merged_exp),
        "project_count": len(merged_proj),
        "career_interests": interests,
    }

    record = CareerPredictionRecord(
        user_id=current_user.id,
        resume_id=resume_row.id if resume_row else None,
        input_profile=input_summary,
        recommendations=result["top_recommendations"],
        model_metadata=result["model_metadata"],
        selected_classifier=result["model_metadata"].get("selected_classifier"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return CareerPredictionResponse(
        prediction_id=record.id,
        resume_id=resume_row.id if resume_row else None,
        resume_file_name=resume_row.file_name if resume_row else None,
        top_recommendations=result["top_recommendations"],
        total_roles_evaluated=result["total_roles_evaluated"],
        disclaimer=result["disclaimer"],
        model_metadata=result["model_metadata"],
        input_summary=input_summary,
        created_at=record.created_at,
    )


def get_latest_career_recommendations(
    current_user: User,
    db: Session,
) -> CareerPredictionResponse:
    """Return the user's latest persisted top-5 career recommendations, or compute from latest resume."""
    latest = (
        db.query(CareerPredictionRecord)
        .filter(CareerPredictionRecord.user_id == current_user.id)
        .order_by(CareerPredictionRecord.created_at.desc(), CareerPredictionRecord.id.desc())
        .first()
    )

    if latest is not None:
        resume_name = None
        if latest.resume_id:
            res_row = db.query(Resume).filter(Resume.id == latest.resume_id).first()
            resume_name = res_row.file_name if res_row else None
        return CareerPredictionResponse(
            prediction_id=latest.id,
            resume_id=latest.resume_id,
            resume_file_name=resume_name,
            top_recommendations=latest.recommendations,
            total_roles_evaluated=12,
            disclaimer=EMPLOYMENT_DISCLAIMER,
            model_metadata=latest.model_metadata or {},
            input_summary=latest.input_profile or {},
            created_at=latest.created_at,
        )

    # If user has uploaded a resume but never clicked predict yet, compute immediately
    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .first()
    )
    if latest_resume is not None:
        return run_career_prediction(
            payload=CareerPredictRequest(resume_id=latest_resume.id),
            current_user=current_user,
            db=db,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No career recommendations yet. Run POST /api/career/predict or upload a resume first.",
    )
