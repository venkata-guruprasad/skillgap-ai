"""JobDescription, SkillGapAnalysis, LearningRoadmap, and RoadmapTask ORM models."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

PortableJSON = JSON().with_variant(JSONB, "postgresql")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Software Engineering", index=True
    )
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    salary_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resume_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    target_role_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("career_roles.id", ondelete="SET NULL"), nullable=True
    )
    job_description_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    match_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    matched_skills: Mapped[Optional[List[Any]]] = mapped_column(PortableJSON, nullable=True)
    missing_skills: Mapped[Optional[List[Any]]] = mapped_column(PortableJSON, nullable=True)
    recommendations: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    analysis_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("skill_gap_analyses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(150), nullable=False, default="Full Stack Developer")
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    estimated_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    generation_mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="deterministic"
    )
    summary_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=True
    )
    milestones: Mapped[List[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=False, default=list
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    roadmap_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    week_label: Mapped[str] = mapped_column(String(40), nullable=False, default="Week 1")
    skill_name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(40), nullable=False, default="study")
    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    resources: Mapped[List[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=False, default=list
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
