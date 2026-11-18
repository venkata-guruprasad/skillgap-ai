"""Export all ORM models so SQLAlchemy Base.metadata registers them for Alembic."""

from app.models.analysis import (
    JobDescription,
    LearningRoadmap,
    RoadmapTask,
    SkillGapAnalysis,
)
from app.models.career_prediction import CareerPredictionRecord
from app.models.career_role import CareerRole, CareerRoleSkill
from app.models.resume import Resume, ResumeSkill
from app.models.skill import Skill
from app.models.user import User

__all__ = [
    "User",
    "Skill",
    "CareerRole",
    "CareerRoleSkill",
    "Resume",
    "ResumeSkill",
    "JobDescription",
    "SkillGapAnalysis",
    "LearningRoadmap",
    "RoadmapTask",
    "CareerPredictionRecord",
]
