"""Pydantic schemas for Personalized AI Learning Roadmap APIs."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RoadmapResourceItem(BaseModel):
    title: str
    source: str
    url: str


class RoadmapGenerateRequest(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=150)
    duration_days: Literal[30, 60, 90] = 30
    resume_id: Optional[int] = None
    analysis_id: Optional[int] = None
    resume_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    weekly_hours: int = Field(default=10, ge=2, le=45)
    learning_style: Literal["balanced", "project-heavy", "fundamentals-first"] = "balanced"
    focus_skills: List[str] = Field(default_factory=list)


class RoadmapTaskResponse(BaseModel):
    id: int
    roadmap_id: int
    phase_number: int
    week_label: str
    skill_name: str
    title: str
    description: Optional[str] = None
    task_type: str
    estimated_hours: int
    resources: List[RoadmapResourceItem] = Field(default_factory=list)
    is_completed: bool
    completed_at: Optional[datetime] = None
    sort_order: int


class RoadmapPhaseDetail(BaseModel):
    phase_number: int
    timeframe: str
    title: str
    skill_name: str
    priority: str
    estimated_hours: int
    learning_objectives: List[str]
    practical_exercises: List[str]
    mini_project: str
    assessment_checkpoint: str
    resources: List[RoadmapResourceItem]
    tasks: List[RoadmapTaskResponse]
    completed_tasks: int
    total_tasks: int
    is_completed: bool


class RoadmapProgressSummary(BaseModel):
    completed_tasks: int
    total_tasks: int
    progress_percent: float
    completed_milestones: int
    total_milestones: int
    remaining_hours: int
    total_hours: int


class RoadmapDetailResponse(BaseModel):
    id: int
    title: str
    target_role: str
    duration_days: int
    estimated_weeks: int
    generation_mode: str
    llm_configured: bool
    summary_explanation: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    progress: RoadmapProgressSummary
    phases: List[RoadmapPhaseDetail]
    created_at: datetime
    updated_at: datetime


class RoadmapListItem(BaseModel):
    id: int
    title: str
    target_role: str
    duration_days: int
    estimated_weeks: int
    generation_mode: str
    is_active: bool
    progress: RoadmapProgressSummary
    created_at: datetime


class RoadmapListResponse(BaseModel):
    total: int
    active_roadmap_id: Optional[int] = None
    items: List[RoadmapListItem]


class RoadmapTaskUpdateRequest(BaseModel):
    is_completed: bool


class RoadmapTaskUpdateResponse(BaseModel):
    task: RoadmapTaskResponse
    roadmap_progress: RoadmapProgressSummary
