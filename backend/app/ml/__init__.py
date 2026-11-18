"""AI/ML and NLP resume & skill gap analysis package (Phases 4 & 5)."""

from app.ml.jd_analyzer import analyze_job_description, segment_jd_sections
from app.ml.nlp_processor import analyze_resume_text, segment_resume_sections
from app.ml.semantic_matcher import (
    compute_document_similarity,
    compute_text_similarity,
    get_active_semantic_model_name,
    match_target_skill,
)
from app.ml.skill_extractor import extract_all_skills
from app.ml.skill_gap_engine import run_skill_gap_engine
from app.ml.skill_taxonomy import SYNONYM_MAP, TECHNICAL_SKILL_DEFINITIONS
from app.ml.text_cleaner import clean_resume_text, redact_pii
from app.ml.text_extractor import (
    EmptyResumeError,
    MalformedDocumentError,
    ResumeExtractionError,
    ScannedDocumentError,
    UnsupportedFileTypeError,
    extract_resume_text,
)

__all__ = [
    "analyze_job_description",
    "segment_jd_sections",
    "analyze_resume_text",
    "clean_resume_text",
    "redact_pii",
    "segment_resume_sections",
    "extract_all_skills",
    "extract_resume_text",
    "compute_document_similarity",
    "compute_text_similarity",
    "get_active_semantic_model_name",
    "match_target_skill",
    "run_skill_gap_engine",
    "SYNONYM_MAP",
    "TECHNICAL_SKILL_DEFINITIONS",
    "ResumeExtractionError",
    "UnsupportedFileTypeError",
    "MalformedDocumentError",
    "ScannedDocumentError",
    "EmptyResumeError",
]
