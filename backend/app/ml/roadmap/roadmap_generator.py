"""Personalized AI & Deterministic 30/60/90-day Learning Roadmap Generator."""

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.config import settings
from app.ml.career.dataset_builder import CAREER_ROLE_CATALOG
from app.ml.roadmap.llm_client import (
    GeneratedPhaseSchema,
    GeneratedRoadmapPlan,
    GeneratedTaskSchema,
    VerifiedResourceSchema,
    generate_roadmap_via_llm,
)
from app.ml.roadmap.resource_catalog import get_skill_curriculum
from app.ml.skill_gap_engine import run_skill_gap_engine

VALID_DURATIONS = {30, 60, 90}


def _find_role_blueprint(target_role: str) -> Dict[str, Any]:
    for role in CAREER_ROLE_CATALOG:
        if role["title"].lower() == target_role.strip().lower():
            return role
    # Partial fallback match
    for role in CAREER_ROLE_CATALOG:
        if target_role.strip().lower() in role["title"].lower():
            return role
    return CAREER_ROLE_CATALOG[4]  # Full Stack Developer default


def _prioritize_target_skills(
    target_role: str,
    resume_skills: Sequence[str],
    explicit_missing_skills: Optional[Sequence[str]],
    focus_skills: Sequence[str],
    duration_days: int,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Determine prioritized skills to cover across roadmap phases."""
    role = _find_role_blueprint(target_role)
    gap = run_skill_gap_engine(
        candidate_skills=resume_skills,
        required_skills=role["required_skills"],
        preferred_skills=role["preferred_skills"],
    )

    ordered: List[Dict[str, Any]] = []
    seen: set[str] = set()

    def _add(name: str, priority: str, reason: str) -> None:
        key = name.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        ordered.append({"name": name.strip(), "priority": priority, "reason": reason})

    # 1. Explicit user focus skills first
    for s in focus_skills:
        _add(s, "Critical", "Explicitly prioritized by your learning preferences.")

    # 2. Explicit missing skills supplied from Skill Gap Engine
    for s in explicit_missing_skills or []:
        _add(s, "Critical", "Identified as a required skill gap for your target role.")

    # 3. Missing required skills from role catalog (sorted by importance weight)
    for item in sorted(gap["missing_required_skills"], key=lambda x: -x["weight"]):
        _add(
            item["skill"],
            "Critical" if item["weight"] >= 1.3 else "High",
            f"Missing required skill (weight {item['weight']}) for {role['title']}.",
        )

    # 4. Missing preferred skills
    for item in gap["missing_preferred_skills"]:
        _add(
            item["skill"],
            "Recommended",
            f"High-value preferred skill differentiating {role['title']} candidates.",
        )

    max_phases = {30: 3, 60: 4, 90: 5}.get(duration_days, 3)

    # 5. If candidate already matches most/all role skills, add mastery/deepening phases up to max_phases
    if len(ordered) < max_phases:
        for req in role["required_skills"]:
            _add(
                req["name"],
                "Mastery",
                f"Deepen production mastery & architecture depth in {req['name']}.",
            )

    selected = ordered[:max_phases]
    prioritized_names = [s["name"] for s in selected]
    return selected, prioritized_names


def _build_deterministic_roadmap(
    target_role: str,
    duration_days: int,
    resume_skills: Sequence[str],
    missing_skills: Optional[Sequence[str]],
    proficiency_evidence: Optional[Dict[str, float]],
    weekly_hours: int,
    learning_style: str,
    focus_skills: Sequence[str],
    precomputed_skills: Optional[Tuple[List[Dict[str, Any]], List[str]]] = None,
) -> GeneratedRoadmapPlan:
    """Deterministic curriculum & verified-resource generator (works with zero external LLM keys)."""
    estimated_weeks = {30: 4, 60: 8, 90: 12}.get(duration_days, 4)
    if precomputed_skills is not None:
        selected_skills, prioritized_names = precomputed_skills
    else:
        selected_skills, prioritized_names = _prioritize_target_skills(
            target_role=target_role,
            resume_skills=resume_skills,
            explicit_missing_skills=missing_skills,
            focus_skills=focus_skills,
            duration_days=duration_days,
        )

    phase_count = len(selected_skills)
    days_per_phase = max(7, duration_days // max(phase_count, 1))
    weeks_per_phase = max(1, math.floor(estimated_weeks / max(phase_count, 1)))

    style_norm = (learning_style or "balanced").strip().lower()
    phases: List[GeneratedPhaseSchema] = []

    current_day = 1
    current_week = 1

    for idx, skill_meta in enumerate(selected_skills, start=1):
        skill_name = skill_meta["name"]
        curriculum = get_skill_curriculum(skill_name)

        end_day = duration_days if idx == phase_count else min(duration_days, current_day + days_per_phase - 1)
        end_week = estimated_weeks if idx == phase_count else min(estimated_weeks, current_week + weeks_per_phase - 1)
        timeframe = f"Days {current_day}-{end_day} (Week {current_week}" + (
            f"-{end_week})" if end_week > current_week else ")"
        )

        # Adapt task hours to user's weekly study hours & proficiency evidence
        prof_score = (proficiency_evidence or {}).get(skill_name, 0.0)
        base_study_hrs = max(2, min(6, round(weekly_hours * 0.35)))
        if prof_score >= 0.7:
            base_study_hrs = max(2, base_study_hrs - 1)
        exercise_hrs = max(2, min(6, round(weekly_hours * 0.3)))
        project_hrs = max(3, min(10, round(weekly_hours * (0.45 if style_norm == "project-heavy" else 0.35))))
        checkpoint_hrs = 2

        w_mid = min(end_week, current_week + (1 if end_week > current_week else 0))

        weekly_tasks = [
            GeneratedTaskSchema(
                week_label=f"Week {current_week}",
                title=f"Study core {skill_name} concepts & official reference patterns",
                description=(
                    f"{curriculum['objectives'][0]} Focus area: {skill_meta['reason']}"
                ),
                task_type="study",
                estimated_hours=base_study_hrs,
            ),
            GeneratedTaskSchema(
                week_label=f"Week {w_mid}",
                title=f"Hands-on practice: {curriculum['exercises'][0]}",
                description=curriculum["exercises"][-1],
                task_type="exercise",
                estimated_hours=exercise_hrs,
            ),
            GeneratedTaskSchema(
                week_label=f"Week {end_week}",
                title=f"Mini Project: {curriculum['mini_project']}",
                description=(
                    f"Build and document a portfolio-ready artifact demonstrating {skill_name} for {target_role}."
                ),
                task_type="mini_project",
                estimated_hours=project_hrs,
            ),
            GeneratedTaskSchema(
                week_label=f"Week {end_week}",
                title=f"Checkpoint: {curriculum['checkpoint']}",
                description=f"Verify readiness before moving to the next phase of your {duration_days}-day plan.",
                task_type="checkpoint",
                estimated_hours=checkpoint_hrs,
            ),
        ]

        # For 60-day and 90-day tracks, include an extra deep-dive integration task
        if duration_days >= 60:
            weekly_tasks.insert(
                2,
                GeneratedTaskSchema(
                    week_label=f"Week {w_mid}",
                    title=f"Applied lab: Integrate {skill_name} with your existing stack",
                    description=(
                        f"Combine {skill_name} with {', '.join(list(resume_skills)[:3]) or 'core engineering tools'} "
                        "following production best practices."
                    ),
                    task_type="exercise",
                    estimated_hours=max(3, exercise_hrs),
                ),
            )

        total_phase_hours = sum(t.estimated_hours for t in weekly_tasks)
        verified_resources = [
            VerifiedResourceSchema.model_validate(r) for r in curriculum["resources"]
        ]

        phases.append(
            GeneratedPhaseSchema(
                phase_number=idx,
                timeframe=timeframe,
                title=f"Phase {idx}: {skill_name} for {target_role}",
                skill_name=skill_name,
                priority=skill_meta["priority"],
                estimated_hours=total_phase_hours,
                learning_objectives=curriculum["objectives"],
                weekly_tasks=weekly_tasks,
                practical_exercises=curriculum["exercises"],
                mini_project=curriculum["mini_project"],
                assessment_checkpoint=curriculum["checkpoint"],
                resources=verified_resources,
            )
        )

        current_day = end_day + 1
        current_week = min(estimated_weeks, end_week + 1)

    existing_preview = ", ".join(list(resume_skills)[:5]) or "your foundational profile"
    summary_explanation = (
        f"This {duration_days}-day ({estimated_weeks}-week) roadmap targets {target_role} "
        f"at ~{weekly_hours} hrs/week ({learning_style} style). Building on {existing_preview}, "
        f"it prioritizes {', '.join(prioritized_names)} through structured objectives, "
        f"hands-on exercises, mini projects, checkpoints, and verified learning resources."
    )

    return GeneratedRoadmapPlan(
        title=f"{duration_days}-Day {target_role} Learning Roadmap",
        target_role=target_role,
        duration_days=duration_days,
        estimated_weeks=estimated_weeks,
        summary_explanation=summary_explanation,
        prioritized_missing_skills=prioritized_names,
        phases=phases,
    )


def generate_personalized_roadmap(
    target_role: str,
    duration_days: int = 30,
    resume_skills: Sequence[str] = (),
    missing_skills: Optional[Sequence[str]] = None,
    proficiency_evidence: Optional[Dict[str, float]] = None,
    weekly_hours: int = 10,
    learning_style: str = "balanced",
    focus_skills: Sequence[str] = (),
) -> Tuple[GeneratedRoadmapPlan, str]:
    """Generate a Pydantic-validated roadmap via configured LLM or deterministic fallback."""
    normalized_duration = duration_days if duration_days in VALID_DURATIONS else 30

    selected_skills, prioritized_missing = _prioritize_target_skills(
        target_role=target_role,
        resume_skills=resume_skills,
        explicit_missing_skills=missing_skills,
        focus_skills=focus_skills,
        duration_days=normalized_duration,
    )

    # Attempt configurable LLM enhancement if credentials are set in environment
    llm_plan = generate_roadmap_via_llm(
        target_role=target_role,
        duration_days=normalized_duration,
        resume_skills=list(resume_skills),
        missing_skills=prioritized_missing,
        weekly_hours=weekly_hours,
        learning_style=learning_style,
    )
    if llm_plan is not None:
        return llm_plan, f"llm_{settings.LLM_PROVIDER.strip().lower()}"

    # Deterministic fallback guarantees full functionality without external LLM keys
    deterministic_plan = _build_deterministic_roadmap(
        target_role=target_role,
        duration_days=normalized_duration,
        resume_skills=resume_skills,
        missing_skills=missing_skills,
        proficiency_evidence=proficiency_evidence,
        weekly_hours=weekly_hours,
        learning_style=learning_style,
        focus_skills=focus_skills,
        precomputed_skills=(selected_skills, prioritized_missing),
    )
    return deterministic_plan, "deterministic"
