"""Pydantic schemas for aggregated live Dashboard Analytics."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DashboardCounts(BaseModel):
    resumes: int = 0
    analyses: int = 0
    career_predictions: int = 0
    roadmaps: int = 0


class DashboardResumeSummary(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size_bytes: int
    ats_score: int = 0
    technical_skill_count: int = 0
    soft_skill_count: int = 0
    created_at: datetime


class DashboardCareerItem(BaseModel):
    career_title: str
    category: str = "Technology"
    avg_salary: str = ""
    compatibility_score: float
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    linked_job_id: Optional[int] = None


class DashboardRoadmapSummary(BaseModel):
    id: int
    title: str
    target_role: str
    duration_days: int
    completed_tasks: int
    total_tasks: int
    completed_milestones: int
    total_milestones: int
    progress_percent: float
    remaining_hours: int
    total_hours: int


class DashboardActivityItem(BaseModel):
    id: str
    type: str
    title: str
    detail: str
    timestamp: datetime


class DashboardAnalyticsResponse(BaseModel):
    counts: DashboardCounts
    latest_resume: Optional[DashboardResumeSummary] = None
    latest_career_recommendations: List[DashboardCareerItem] = Field(default_factory=list)
    active_roadmap: Optional[DashboardRoadmapSummary] = None
    recent_activity: List[DashboardActivityItem] = Field(default_factory=list)
