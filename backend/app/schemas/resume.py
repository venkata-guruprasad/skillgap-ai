"""Pydantic schemas for resume upload, analysis, history, and skill extraction."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExtractedSkillItem(BaseModel):
    name: str
    category: str
    confidence: float
    confirmed: bool = True
    matched_terms: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class RedactedPersonalInfo(BaseModel):
    name_detected: bool = False
    masked_name: Optional[str] = None
    email_detected: bool = False
    masked_email: Optional[str] = None
    phone_detected: bool = False
    masked_phone: Optional[str] = None
    pii_redacted: bool = True


class EducationEntry(BaseModel):
    degree: str
    institution: Optional[str] = None
    period: Optional[str] = None
    details: Optional[str] = None


class ExperienceEntry(BaseModel):
    role: str
    organization: Optional[str] = None
    duration: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    title: str
    description: str = ""
    technologies: List[str] = Field(default_factory=list)


class AnalysisSummary(BaseModel):
    word_count: int = 0
    ats_score: int = 0
    sections_detected: List[str] = Field(default_factory=list)
    technical_skill_count: int = 0
    soft_skill_count: int = 0
    education_count: int = 0
    experience_count: int = 0
    project_count: int = 0
    certification_count: int = 0
    recommendations: List[str] = Field(default_factory=list)


class ResumeAnalysisPayload(BaseModel):
    cleaned_text_preview: str = ""
    personal_info: RedactedPersonalInfo = Field(default_factory=RedactedPersonalInfo)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    technical_skills: List[ExtractedSkillItem] = Field(default_factory=list)
    soft_skills: List[ExtractedSkillItem] = Field(default_factory=list)
    unconfirmed_mentions: List[ExtractedSkillItem] = Field(default_factory=list)
    skills_by_category: Dict[str, List[ExtractedSkillItem]] = Field(default_factory=dict)
    summary: AnalysisSummary = Field(default_factory=AnalysisSummary)


class ResumeDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    file_type: str
    file_size_bytes: Optional[int] = None
    extraction_status: str
    page_count: Optional[int] = None
    created_at: datetime
    analysis: ResumeAnalysisPayload


class ResumeHistoryItem(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size_bytes: Optional[int] = None
    extraction_status: str
    technical_skill_count: int = 0
    soft_skill_count: int = 0
    ats_score: int = 0
    created_at: datetime


class ResumeHistoryResponse(BaseModel):
    total: int
    items: List[ResumeHistoryItem]


class ResumeDeleteResponse(BaseModel):
    status: str = "success"
    message: str
    deleted_id: int


class SkillExtractRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=100_000)


class SkillExtractResponse(BaseModel):
    technical_skills: List[ExtractedSkillItem]
    soft_skills: List[ExtractedSkillItem]
    unconfirmed_mentions: List[ExtractedSkillItem]
    skills_by_category: Dict[str, List[ExtractedSkillItem]]
    total_confirmed: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
