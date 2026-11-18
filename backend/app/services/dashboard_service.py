"""Aggregated live Dashboard Analytics service built from persisted user records."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.analysis import LearningRoadmap, RoadmapTask, SkillGapAnalysis
from app.models.career_prediction import CareerPredictionRecord
from app.models.resume import Resume
from app.models.user import User
from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardAnalyticsResponse,
    DashboardCareerItem,
    DashboardCounts,
    DashboardResumeSummary,
    DashboardRoadmapSummary,
)
from app.services.roadmap_service import _compute_progress


def _normalize_dt(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def build_dashboard_analytics(
    current_user: User,
    db: Session,
) -> DashboardAnalyticsResponse:
    """Aggregate real counts, latest resume, ML career predictions, active roadmap, and activity feed."""
    resume_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    analysis_count = (
        db.query(SkillGapAnalysis)
        .filter(SkillGapAnalysis.user_id == current_user.id)
        .count()
    )
    prediction_count = (
        db.query(CareerPredictionRecord)
        .filter(CareerPredictionRecord.user_id == current_user.id)
        .count()
    )
    roadmap_count = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == current_user.id)
        .count()
    )

    counts = DashboardCounts(
        resumes=resume_count,
        analyses=analysis_count,
        career_predictions=prediction_count,
        roadmaps=roadmap_count,
    )

    # Latest resume
    latest_resume_row = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .first()
    )
    latest_resume: Optional[DashboardResumeSummary] = None
    if latest_resume_row is not None:
        parsed = latest_resume_row.parsed_data or {}
        summary = parsed.get("summary") or {}
        latest_resume = DashboardResumeSummary(
            id=latest_resume_row.id,
            file_name=latest_resume_row.file_name,
            file_type=latest_resume_row.file_type,
            file_size_bytes=latest_resume_row.file_size_bytes or 0,
            ats_score=int(summary.get("ats_score", 0)),
            technical_skill_count=len(parsed.get("technical_skills", [])),
            soft_skill_count=len(parsed.get("soft_skills", [])),
            created_at=_normalize_dt(latest_resume_row.created_at),
        )

    # Latest ML Career Prediction recommendations
    latest_pred_row = (
        db.query(CareerPredictionRecord)
        .filter(CareerPredictionRecord.user_id == current_user.id)
        .order_by(CareerPredictionRecord.created_at.desc(), CareerPredictionRecord.id.desc())
        .first()
    )
    career_items: List[DashboardCareerItem] = []
    if latest_pred_row is not None:
        for rec in (latest_pred_row.recommendations or [])[:5]:
            if isinstance(rec, dict) and rec.get("career_title"):
                career_items.append(
                    DashboardCareerItem(
                        career_title=rec["career_title"],
                        category=rec.get("category", "Technology"),
                        avg_salary=rec.get("avg_salary", ""),
                        compatibility_score=float(rec.get("compatibility_score", 0.0)),
                        matching_skills=list(rec.get("matching_skills") or []),
                        missing_skills=list(rec.get("missing_skills") or []),
                        linked_job_id=rec.get("linked_job_id"),
                    )
                )

    # Active learning roadmap summary
    active_rm_row = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == current_user.id)
        .order_by(
            LearningRoadmap.is_active.desc(),
            LearningRoadmap.created_at.desc(),
            LearningRoadmap.id.desc(),
        )
        .first()
    )
    active_roadmap: Optional[DashboardRoadmapSummary] = None
    completed_tasks_for_feed: List[RoadmapTask] = []
    if active_rm_row is not None:
        rm_tasks = (
            db.query(RoadmapTask)
            .filter(RoadmapTask.roadmap_id == active_rm_row.id)
            .order_by(RoadmapTask.sort_order.asc(), RoadmapTask.id.asc())
            .all()
        )
        prog = _compute_progress(active_rm_row.milestones or [], rm_tasks)
        active_roadmap = DashboardRoadmapSummary(
            id=active_rm_row.id,
            title=active_rm_row.title,
            target_role=active_rm_row.target_role,
            duration_days=active_rm_row.duration_days,
            completed_tasks=prog.completed_tasks,
            total_tasks=prog.total_tasks,
            completed_milestones=prog.completed_milestones,
            total_milestones=prog.total_milestones,
            progress_percent=prog.progress_percent,
            remaining_hours=prog.remaining_hours,
            total_hours=prog.total_hours,
        )
        completed_tasks_for_feed = [t for t in rm_tasks if t.is_completed and t.completed_at]

    # Real recent activity feed from DB records
    activity: List[DashboardActivityItem] = []

    recent_resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .limit(3)
        .all()
    )
    for r in recent_resumes:
        tech_cnt = len((r.parsed_data or {}).get("technical_skills", []))
        activity.append(
            DashboardActivityItem(
                id=f"resume-{r.id}",
                type="resume",
                title=f"Analyzed resume: {r.file_name}",
                detail=f"Extracted {tech_cnt} technical skills ({r.file_type})",
                timestamp=_normalize_dt(r.created_at),
            )
        )

    recent_analyses = (
        db.query(SkillGapAnalysis)
        .filter(SkillGapAnalysis.user_id == current_user.id)
        .order_by(SkillGapAnalysis.created_at.desc(), SkillGapAnalysis.id.desc())
        .limit(3)
        .all()
    )
    for a in recent_analyses:
        rec_meta = a.recommendations or {}
        job_title = rec_meta.get("job_title", "Target Role")
        score = float(a.match_score or 0)
        activity.append(
            DashboardActivityItem(
                id=f"analysis-{a.id}",
                type="skill_gap",
                title=f"Skill gap analyzed: {job_title}",
                detail=f"{score:.1f}% required match · {len(a.missing_skills or [])} missing required skills",
                timestamp=_normalize_dt(a.created_at),
            )
        )

    if latest_pred_row is not None and career_items:
        top = career_items[0]
        activity.append(
            DashboardActivityItem(
                id=f"career-{latest_pred_row.id}",
                type="career",
                title=f"ML career match: {top.career_title}",
                detail=f"{top.compatibility_score:.1f}% compatibility across 12 roles",
                timestamp=_normalize_dt(latest_pred_row.created_at),
            )
        )

    if active_rm_row is not None:
        activity.append(
            DashboardActivityItem(
                id=f"roadmap-{active_rm_row.id}",
                type="roadmap",
                title=f"Active plan: {active_rm_row.title}",
                detail=(
                    f"{active_roadmap.completed_tasks}/{active_roadmap.total_tasks} tasks completed "
                    f"({active_roadmap.progress_percent}%)"
                    if active_roadmap
                    else f"{active_rm_row.duration_days}-day plan"
                ),
                timestamp=_normalize_dt(active_rm_row.created_at),
            )
        )

    for t in sorted(
        completed_tasks_for_feed,
        key=lambda x: _normalize_dt(x.completed_at),
        reverse=True,
    )[:3]:
        activity.append(
            DashboardActivityItem(
                id=f"task-{t.id}",
                type="task",
                title=f"Completed task: {t.title}",
                detail=f"{t.skill_name} · {t.week_label} ({t.estimated_hours}h)",
                timestamp=_normalize_dt(t.completed_at),
            )
        )

    activity.sort(key=lambda item: item.timestamp, reverse=True)

    return DashboardAnalyticsResponse(
        counts=counts,
        latest_resume=latest_resume,
        latest_career_recommendations=career_items,
        active_roadmap=active_roadmap,
        recent_activity=activity[:8],
    )
