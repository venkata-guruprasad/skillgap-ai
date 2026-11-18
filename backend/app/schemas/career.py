"""Pydantic schemas for ML Career Prediction APIs."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CareerPredictRequest(BaseModel):
    resume_id: Optional[int] = None
    resume_skills: Optional[List[str]] = None
    education: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    career_interests: List[str] = Field(default_factory=list)


class CareerScoreBreakdown(BaseModel):
    skill_gap_score: float
    preferred_skill_score: Optional[float] = None
    ml_classifier_score: float
    ml_raw_probability: float
    semantic_similarity: float
    interest_bonus: float = 0.0


class CareerRecommendationItem(BaseModel):
    career_title: str
    category: str
    avg_salary: str
    demand_level: str
    role_description: str
    compatibility_score: float
    score_breakdown: CareerScoreBreakdown
    matching_skills: List[str]
    missing_skills: List[str]
    required_additional_skills: List[str]
    candidate_additional_skills: List[str] = Field(default_factory=list)
    explanation: str
    linked_job_id: Optional[int] = None


class CareerPredictionResponse(BaseModel):
    prediction_id: Optional[int] = None
    resume_id: Optional[int] = None
    resume_file_name: Optional[str] = None
    top_recommendations: List[CareerRecommendationItem]
    total_roles_evaluated: int
    disclaimer: str
    model_metadata: Dict[str, Any] = Field(default_factory=dict)
    input_summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
