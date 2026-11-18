"""Pydantic schemas for Job Descriptions and Skill Gap Analysis APIs."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class JobSkillItem(BaseModel):
    name: str
    category: str = "General"
    weight: float = 1.0
    priority: str = "Required"
    evidence: List[str] = Field(default_factory=list)


class JobExtractedPayload(BaseModel):
    required_skills: List[JobSkillItem] = Field(default_factory=list)
    preferred_skills: List[JobSkillItem] = Field(default_factory=list)
    soft_skills: List[Dict[str, Any]] = Field(default_factory=list)
    experience_requirements: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="Software Engineering", min_length=2, max_length=100)
    raw_text: str = Field(..., min_length=30, max_length=50_000)
    location: Optional[str] = Field(default=None, max_length=150)
    work_mode: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)
    salary_range: Optional[str] = Field(default=None, max_length=100)


class JobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: Optional[str] = None
    category: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    is_sample: bool = False
    raw_text: str
    extracted: JobExtractedPayload
    created_at: datetime


class JobListItem(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    category: str
    location: Optional[str] = None
    work_mode: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    is_sample: bool = False
    required_skills: List[JobSkillItem] = Field(default_factory=list)
    preferred_skills: List[JobSkillItem] = Field(default_factory=list)
    required_skill_count: int = 0
    preferred_skill_count: int = 0
    created_at: datetime


class JobListResponse(BaseModel):
    total: int
    items: List[JobListItem]


class SkillGapRequest(BaseModel):
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    candidate_skills: Optional[List[str]] = None
    custom_job: Optional[JobCreateRequest] = None


class MatchedSkillDetail(BaseModel):
    skill: str
    category: str
    weight: float
    priority: str
    match_type: str
    matched_with: Optional[str] = None
    similarity: float


class MissingSkillDetail(BaseModel):
    skill: str
    category: str
    weight: float
    priority: str
    closest_candidate_skill: Optional[str] = None
    closest_similarity: float = 0.0


class AdditionalSkillDetail(BaseModel):
    skill: str
    original_name: str
    category: str


class CategoryBreakdownItem(BaseModel):
    category: str
    matched_required: int
    missing_required: int
    matched_preferred: int
    missing_preferred: int
    coverage_percent: float


class RadarPointItem(BaseModel):
    domain: str
    candidate: float
    required: float


class ScoreExplanation(BaseModel):
    formula: str
    matched_required_weight: float
    total_required_weight: float
    compatibility_score: float
    matched_preferred_weight: float
    total_preferred_weight: float
    preferred_score: Optional[float] = None
    jd_semantic_similarity: float
    semantic_model: str
    summary_text: str


class SkillGapDetailResponse(BaseModel):
    id: int
    resume_id: Optional[int] = None
    resume_file_name: Optional[str] = None
    job_id: int
    job_title: str
    job_company: Optional[str] = None
    job_category: str
    is_sample_job: bool = False
    compatibility_score: float
    preferred_score: Optional[float] = None
    jd_semantic_similarity: float
    matched_required_skills: List[MatchedSkillDetail]
    missing_required_skills: List[MissingSkillDetail]
    matched_preferred_skills: List[MatchedSkillDetail]
    missing_preferred_skills: List[MissingSkillDetail]
    additional_skills: List[AdditionalSkillDetail]
    category_breakdown: List[CategoryBreakdownItem]
    radar_data: List[RadarPointItem]
    score_explanation: ScoreExplanation
    job_details: JobExtractedPayload
    created_at: datetime


class SkillGapHistoryItem(BaseModel):
    id: int
    resume_id: Optional[int] = None
    resume_file_name: Optional[str] = None
    job_id: Optional[int] = None
    job_title: str
    job_company: Optional[str] = None
    job_category: str
    is_sample_job: bool = False
    compatibility_score: float
    preferred_score: Optional[float] = None
    jd_semantic_similarity: float = 0.0
    matched_required_count: int = 0
    missing_required_count: int = 0
    additional_skill_count: int = 0
    created_at: datetime


class SkillGapHistoryResponse(BaseModel):
    total: int
    items: List[SkillGapHistoryItem]
