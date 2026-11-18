"""Business logic for Personalized AI Learning Roadmap generation, persistence, and progress tracking."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.roadmap.llm_client import is_llm_configured
from app.ml.roadmap.roadmap_generator import generate_personalized_roadmap
from app.models.analysis import LearningRoadmap, RoadmapTask, SkillGapAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapDetailResponse,
    RoadmapGenerateRequest,
    RoadmapListItem,
    RoadmapListResponse,
    RoadmapPhaseDetail,
    RoadmapProgressSummary,
    RoadmapTaskResponse,
    RoadmapTaskUpdateResponse,
)


def _compute_progress(
    milestones: List[Dict[str, Any]],
    tasks: List[RoadmapTask],
) -> RoadmapProgressSummary:
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    progress_percent = (
        round((completed_tasks / total_tasks) * 100.0, 1) if total_tasks > 0 else 0.0
    )
    total_hours = sum(t.estimated_hours or 0 for t in tasks)
    remaining_hours = sum((t.estimated_hours or 0) for t in tasks if not t.is_completed)

    total_milestones = len(milestones)
    completed_milestones = 0
    for phase in milestones:
        p_num = phase.get("phase_number")
        p_tasks = [t for t in tasks if t.phase_number == p_num]
        if p_tasks and all(t.is_completed for t in p_tasks):
            completed_milestones += 1

    return RoadmapProgressSummary(
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
        progress_percent=progress_percent,
        completed_milestones=completed_milestones,
        total_milestones=total_milestones,
        remaining_hours=remaining_hours,
        total_hours=total_hours,
    )


def _to_task_response(task: RoadmapTask) -> RoadmapTaskResponse:
    return RoadmapTaskResponse(
        id=task.id,
        roadmap_id=task.roadmap_id,
        phase_number=task.phase_number,
        week_label=task.week_label,
        skill_name=task.skill_name,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        estimated_hours=task.estimated_hours,
        resources=task.resources or [],
        is_completed=bool(task.is_completed),
        completed_at=task.completed_at,
        sort_order=task.sort_order,
    )


def _to_roadmap_detail(
    roadmap: LearningRoadmap,
    tasks: List[RoadmapTask],
) -> RoadmapDetailResponse:
    milestones = roadmap.milestones or []
    progress = _compute_progress(milestones, tasks)

    phases: List[RoadmapPhaseDetail] = []
    for phase in milestones:
        p_num = phase["phase_number"]
        p_tasks = sorted(
            [t for t in tasks if t.phase_number == p_num],
            key=lambda x: (x.sort_order, x.id),
        )
        p_done = sum(1 for t in p_tasks if t.is_completed)
        phases.append(
            RoadmapPhaseDetail(
                phase_number=p_num,
                timeframe=phase["timeframe"],
                title=phase["title"],
                skill_name=phase["skill_name"],
                priority=phase.get("priority", "High"),
                estimated_hours=phase.get("estimated_hours", sum(t.estimated_hours for t in p_tasks)),
                learning_objectives=phase.get("learning_objectives", []),
                practical_exercises=phase.get("practical_exercises", []),
                mini_project=phase.get("mini_project", ""),
                assessment_checkpoint=phase.get("assessment_checkpoint", ""),
                resources=phase.get("resources", []),
                tasks=[_to_task_response(t) for t in p_tasks],
                completed_tasks=p_done,
                total_tasks=len(p_tasks),
                is_completed=bool(p_tasks) and p_done == len(p_tasks),
            )
        )

    return RoadmapDetailResponse(
        id=roadmap.id,
        title=roadmap.title,
        target_role=roadmap.target_role,
        duration_days=roadmap.duration_days,
        estimated_weeks=roadmap.estimated_weeks or max(4, roadmap.duration_days // 7),
        generation_mode=roadmap.generation_mode,
        llm_configured=is_llm_configured(),
        summary_explanation=roadmap.summary_explanation or "",
        preferences=roadmap.preferences or {},
        is_active=bool(roadmap.is_active),
        progress=progress,
        phases=phases,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at,
    )


def _resolve_inputs(
    payload: RoadmapGenerateRequest,
    current_user: User,
    db: Session,
) -> Tuple[List[str], Optional[List[str]], Dict[str, float], Optional[int]]:
    """Gather resume skills, proficiency evidence, and missing skills from DB records or payload."""
    resume_skills: List[str] = list(payload.resume_skills or [])
    missing_skills: Optional[List[str]] = (
        list(payload.missing_skills) if payload.missing_skills else None
    )
    proficiency_evidence: Dict[str, float] = {}
    linked_analysis_id: Optional[int] = None

    # Resolve Resume if provided or latest uploaded resume
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
                detail="Selected resume not found in your account.",
            )
    elif not resume_skills:
        resume_row = (
            db.query(Resume)
            .filter(Resume.user_id == current_user.id)
            .order_by(Resume.created_at.desc(), Resume.id.desc())
            .first()
        )

    if resume_row is not None:
        parsed = resume_row.parsed_data or {}
        for item in parsed.get("technical_skills", []):
            if isinstance(item, dict) and item.get("name"):
                proficiency_evidence[item["name"]] = float(item.get("confidence", 0.8))
                if not payload.resume_skills:
                    resume_skills.append(item["name"])

    # Resolve SkillGapAnalysis if explicitly requested
    if payload.analysis_id is not None:
        analysis_row = (
            db.query(SkillGapAnalysis)
            .filter(
                SkillGapAnalysis.id == payload.analysis_id,
                SkillGapAnalysis.user_id == current_user.id,
            )
            .first()
        )
        if analysis_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected skill gap analysis not found in your account.",
            )
        linked_analysis_id = analysis_row.id
        if missing_skills is None:
            missing_skills = [
                item["skill"]
                for item in (analysis_row.missing_skills or [])
                if isinstance(item, dict) and item.get("skill")
            ]

    return (
        list(dict.fromkeys(s.strip() for s in resume_skills if s and s.strip())),
        missing_skills,
        proficiency_evidence,
        linked_analysis_id,
    )


def create_generated_roadmap(
    payload: RoadmapGenerateRequest,
    current_user: User,
    db: Session,
) -> RoadmapDetailResponse:
    """Generate and persist a personalized 30/60/90-day roadmap and its trackable tasks."""
    resume_skills, missing_skills, proficiency, linked_analysis_id = _resolve_inputs(
        payload, current_user, db
    )

    plan, generation_mode = generate_personalized_roadmap(
        target_role=payload.target_role.strip(),
        duration_days=payload.duration_days,
        resume_skills=resume_skills,
        missing_skills=missing_skills,
        proficiency_evidence=proficiency,
        weekly_hours=payload.weekly_hours,
        learning_style=payload.learning_style,
        focus_skills=payload.focus_skills,
    )

    # Demote previous active roadmaps so learning history is preserved cleanly
    db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == current_user.id,
        LearningRoadmap.is_active.is_(True),
    ).update({"is_active": False})

    milestones_json: List[Dict[str, Any]] = []
    for phase in plan.phases:
        milestones_json.append(
            {
                "phase_number": phase.phase_number,
                "timeframe": phase.timeframe,
                "title": phase.title,
                "skill_name": phase.skill_name,
                "priority": phase.priority,
                "estimated_hours": phase.estimated_hours,
                "learning_objectives": phase.learning_objectives,
                "practical_exercises": phase.practical_exercises,
                "mini_project": phase.mini_project,
                "assessment_checkpoint": phase.assessment_checkpoint,
                "resources": [r.model_dump() for r in phase.resources],
            }
        )

    roadmap_row = LearningRoadmap(
        user_id=current_user.id,
        analysis_id=linked_analysis_id,
        title=plan.title,
        target_role=plan.target_role,
        duration_days=plan.duration_days,
        estimated_weeks=plan.estimated_weeks,
        generation_mode=generation_mode,
        summary_explanation=plan.summary_explanation,
        preferences={
            "weekly_hours": payload.weekly_hours,
            "learning_style": payload.learning_style,
            "focus_skills": payload.focus_skills,
            "prioritized_missing_skills": plan.prioritized_missing_skills,
            "resume_skills_used": resume_skills,
        },
        milestones=milestones_json,
        is_active=True,
    )
    db.add(roadmap_row)
    db.flush()

    created_tasks: List[RoadmapTask] = []
    sort_idx = 0
    for phase in plan.phases:
        phase_resources = [r.model_dump() for r in phase.resources]
        for task in phase.weekly_tasks:
            sort_idx += 1
            row = RoadmapTask(
                roadmap_id=roadmap_row.id,
                phase_number=phase.phase_number,
                week_label=task.week_label,
                skill_name=phase.skill_name,
                title=task.title,
                description=task.description,
                task_type=task.task_type,
                estimated_hours=task.estimated_hours,
                resources=phase_resources,
                is_completed=False,
                sort_order=sort_idx,
            )
            db.add(row)
            created_tasks.append(row)

    db.commit()
    db.refresh(roadmap_row)
    for t in created_tasks:
        db.refresh(t)

    return _to_roadmap_detail(roadmap_row, created_tasks)


def list_user_roadmaps(
    current_user: User,
    db: Session,
) -> RoadmapListResponse:
    """Return all generated roadmaps (learning history) owned by the authenticated user."""
    roadmaps = (
        db.query(LearningRoadmap)
        .filter(LearningRoadmap.user_id == current_user.id)
        .order_by(
            LearningRoadmap.is_active.desc(),
            LearningRoadmap.created_at.desc(),
            LearningRoadmap.id.desc(),
        )
        .all()
    )

    items: List[RoadmapListItem] = []
    active_id: Optional[int] = None

    # Batch-fetch all tasks for user's roadmaps in a single query (eliminates N+1)
    roadmap_ids = [rm.id for rm in roadmaps]
    tasks_by_roadmap: Dict[int, List[RoadmapTask]] = {rid: [] for rid in roadmap_ids}
    if roadmap_ids:
        all_tasks = (
            db.query(RoadmapTask)
            .filter(RoadmapTask.roadmap_id.in_(roadmap_ids))
            .order_by(RoadmapTask.sort_order.asc(), RoadmapTask.id.asc())
            .all()
        )
        for task in all_tasks:
            tasks_by_roadmap[task.roadmap_id].append(task)

    for rm in roadmaps:
        if rm.is_active and active_id is None:
            active_id = rm.id
        tasks = tasks_by_roadmap.get(rm.id, [])
        progress = _compute_progress(rm.milestones or [], tasks)
        items.append(
            RoadmapListItem(
                id=rm.id,
                title=rm.title,
                target_role=rm.target_role,
                duration_days=rm.duration_days,
                estimated_weeks=rm.estimated_weeks or max(4, rm.duration_days // 7),
                generation_mode=rm.generation_mode,
                is_active=bool(rm.is_active),
                progress=progress,
                created_at=rm.created_at,
            )
        )

    if active_id is None and items:
        active_id = items[0].id

    return RoadmapListResponse(total=len(items), active_roadmap_id=active_id, items=items)


def get_user_roadmap_by_id(
    roadmap_id: int,
    current_user: User,
    db: Session,
) -> RoadmapDetailResponse:
    """Retrieve a specific owned roadmap with all phases, resources, and tasks."""
    roadmap = (
        db.query(LearningRoadmap)
        .filter(
            LearningRoadmap.id == roadmap_id,
            LearningRoadmap.user_id == current_user.id,
        )
        .first()
    )
    if roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning roadmap not found.",
        )

    tasks = (
        db.query(RoadmapTask)
        .filter(RoadmapTask.roadmap_id == roadmap.id)
        .order_by(RoadmapTask.sort_order.asc(), RoadmapTask.id.asc())
        .all()
    )
    return _to_roadmap_detail(roadmap, tasks)


def update_user_roadmap_task(
    task_id: int,
    is_completed: bool,
    current_user: User,
    db: Session,
) -> RoadmapTaskUpdateResponse:
    """Toggle completion status on an owned roadmap task and persist to database."""
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap task not found.",
        )

    roadmap = (
        db.query(LearningRoadmap)
        .filter(
            LearningRoadmap.id == task.roadmap_id,
            LearningRoadmap.user_id == current_user.id,
        )
        .first()
    )
    if roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap task not found.",
        )

    task.is_completed = bool(is_completed)
    task.completed_at = datetime.now(timezone.utc) if is_completed else None
    if not roadmap.is_active:
        db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.is_active.is_(True),
        ).update({"is_active": False})
        roadmap.is_active = True
    db.commit()
    db.refresh(task)

    all_tasks = (
        db.query(RoadmapTask)
        .filter(RoadmapTask.roadmap_id == roadmap.id)
        .order_by(RoadmapTask.sort_order.asc(), RoadmapTask.id.asc())
        .all()
    )
    progress = _compute_progress(roadmap.milestones or [], all_tasks)

    return RoadmapTaskUpdateResponse(
        task=_to_task_response(task),
        roadmap_progress=progress,
    )
