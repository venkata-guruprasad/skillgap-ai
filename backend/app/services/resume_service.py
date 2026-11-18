"""Business logic for secure resume upload, NLP analysis, persistence, and history."""

from decimal import Decimal
import hashlib
from pathlib import Path
import re
from typing import List, Optional
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.ml.nlp_processor import analyze_resume_text, segment_resume_sections
from app.ml.skill_extractor import extract_all_skills
from app.ml.text_cleaner import clean_resume_text
from app.ml.text_extractor import (
    EmptyResumeError,
    MalformedDocumentError,
    ScannedDocumentError,
    UnsupportedFileTypeError,
    extract_resume_text,
)
from app.models.resume import Resume, ResumeSkill
from app.models.skill import Skill
from app.models.user import User
from app.schemas.resume import (
    ResumeAnalysisPayload,
    ResumeDeleteResponse,
    ResumeDetailResponse,
    ResumeHistoryItem,
    ResumeHistoryResponse,
    SkillExtractResponse,
)

SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(filename: Optional[str]) -> str:
    base = Path(filename or "resume.pdf").name
    sanitized = SAFE_FILENAME_PATTERN.sub("_", base).strip("._")
    return sanitized[:180] or "resume.pdf"


def _persist_file_securely(user_id: int, safe_filename: str, content: bytes) -> str:
    """Save uploaded resume bytes under user-scoped private upload directory."""
    user_dir = Path(settings.UPLOAD_DIR).resolve() / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{safe_filename}"
    target_path = (user_dir / unique_name).resolve()

    # Prevent any path traversal outside user_dir
    if user_dir not in target_path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid upload filename.",
        )

    target_path.write_bytes(content)
    return str(target_path)


def _sync_resume_skills(
    db: Session,
    resume_id: int,
    technical_skills: List[dict],
) -> None:
    """Upsert canonical Skill records and link confirmed skills to ResumeSkill rows."""
    for skill_item in technical_skills:
        skill_name = skill_item["name"]
        skill_category = skill_item.get("category", "General")
        confidence = Decimal(str(round(float(skill_item.get("confidence", 0.8)), 4)))

        skill_row = db.query(Skill).filter(Skill.name == skill_name).first()
        if skill_row is None:
            skill_row = Skill(name=skill_name, category=skill_category)
            db.add(skill_row)
            db.flush()

        existing_link = (
            db.query(ResumeSkill)
            .filter(
                ResumeSkill.resume_id == resume_id,
                ResumeSkill.skill_id == skill_row.id,
            )
            .first()
        )
        if existing_link is None:
            db.add(
                ResumeSkill(
                    resume_id=resume_id,
                    skill_id=skill_row.id,
                    confidence_score=confidence,
                    source="nlp_extracted",
                )
            )


def _to_detail_response(resume: Resume) -> ResumeDetailResponse:
    parsed = resume.parsed_data or {}
    page_count = parsed.get("page_count")
    analysis_dict = {k: v for k, v in parsed.items() if k != "page_count"}
    analysis = ResumeAnalysisPayload.model_validate(analysis_dict)
    return ResumeDetailResponse(
        id=resume.id,
        file_name=resume.file_name,
        file_type=resume.file_type,
        file_size_bytes=resume.file_size_bytes,
        extraction_status=resume.extraction_status,
        page_count=page_count,
        created_at=resume.created_at,
        analysis=analysis,
    )


async def upload_and_analyze_resume(
    file: UploadFile,
    current_user: User,
    db: Session,
) -> ResumeDetailResponse:
    """Validate, securely store, extract text, run NLP skill analysis, and persist resume."""
    safe_filename = _sanitize_filename(file.filename)

    # Read up to MAX_UPLOAD_SIZE_BYTES + 1 byte to reject oversized files without unbounded RAM use
    max_bytes = settings.MAX_UPLOAD_SIZE_BYTES
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {max_bytes // (1024 * 1024)} MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uploaded file is empty.",
        )

    # Check duplicate upload per user via SHA-256 content hash
    file_hash = hashlib.sha256(content).hexdigest()
    existing_duplicate = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id, Resume.file_hash == file_hash)
        .first()
    )
    if existing_duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": (
                    f"This exact resume ('{existing_duplicate.file_name}') has already been "
                    "uploaded and analyzed."
                ),
                "existing_resume_id": existing_duplicate.id,
                "existing_file_name": existing_duplicate.file_name,
            },
        )

    # Extract & validate document structure using PyMuPDF / python-docx
    try:
        extraction = extract_resume_text(
            filename=safe_filename,
            file_bytes=content,
            content_type=file.content_type,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (MalformedDocumentError, ScannedDocumentError, EmptyResumeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    # Clean text and enforce minimum readable content threshold
    cleaned_text = clean_resume_text(extraction.raw_text)
    if sum(1 for ch in cleaned_text if ch.isalnum()) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Resume contains insufficient readable text after cleaning.",
        )

    # Run full NLP processing & skill extraction
    analysis_data = analyze_resume_text(extraction.raw_text)
    analysis_data["page_count"] = extraction.page_count

    # Persist file securely on disk ONLY after validation & extraction succeed
    stored_path = _persist_file_securely(current_user.id, safe_filename, content)

    resume_row = Resume(
        user_id=current_user.id,
        file_name=safe_filename,
        file_type=extraction.file_type.upper(),
        file_path=stored_path,
        file_size_bytes=len(content),
        file_hash=file_hash,
        extraction_status="completed",
        raw_text=cleaned_text,
        parsed_data=analysis_data,
    )
    db.add(resume_row)
    db.flush()

    _sync_resume_skills(db, resume_row.id, analysis_data.get("technical_skills", []))
    db.commit()
    db.refresh(resume_row)

    return _to_detail_response(resume_row)


def list_user_resumes(current_user: User, db: Session) -> ResumeHistoryResponse:
    """Return resume upload history belonging strictly to the authenticated user."""
    rows = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .all()
    )

    items = []
    for row in rows:
        parsed = row.parsed_data or {}
        summary = parsed.get("summary", {})
        items.append(
            ResumeHistoryItem(
                id=row.id,
                file_name=row.file_name,
                file_type=row.file_type,
                file_size_bytes=row.file_size_bytes,
                extraction_status=row.extraction_status,
                technical_skill_count=summary.get(
                    "technical_skill_count",
                    len(parsed.get("technical_skills", [])),
                ),
                soft_skill_count=summary.get(
                    "soft_skill_count",
                    len(parsed.get("soft_skills", [])),
                ),
                ats_score=summary.get("ats_score", 0),
                created_at=row.created_at,
            )
        )

    return ResumeHistoryResponse(total=len(items), items=items)


def get_user_resume_by_id(
    resume_id: int,
    current_user: User,
    db: Session,
) -> ResumeDetailResponse:
    """Fetch a single resume analysis enforcing owner-only access."""
    row = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return _to_detail_response(row)


def delete_user_resume_by_id(
    resume_id: int,
    current_user: User,
    db: Session,
) -> ResumeDeleteResponse:
    """Delete a resume record and its stored file from disk (owner-only)."""
    row = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    file_path = row.file_path
    file_name = row.file_name
    db.delete(row)
    db.commit()

    # Best-effort secure removal of stored file
    if file_path:
        try:
            path_obj = Path(file_path).resolve()
            upload_root = Path(settings.UPLOAD_DIR).resolve()
            if upload_root in path_obj.parents and path_obj.exists():
                path_obj.unlink()
        except OSError:
            pass

    return ResumeDeleteResponse(
        status="success",
        message=f"Resume '{file_name}' deleted successfully.",
        deleted_id=resume_id,
    )


def extract_skills_from_raw_text(text: str) -> SkillExtractResponse:
    """Run cleaning, sectioning, and evidence-backed skill extraction on arbitrary text."""
    cleaned = clean_resume_text(text)
    if sum(1 for ch in cleaned if ch.isalnum()) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Input text contains insufficient readable content for skill extraction.",
        )

    sections = segment_resume_sections(cleaned)
    extracted = extract_all_skills(sections=sections, full_text=cleaned)
    return SkillExtractResponse(
        technical_skills=extracted["technical_skills"],
        soft_skills=extracted["soft_skills"],
        unconfirmed_mentions=extracted["unconfirmed_mentions"],
        skills_by_category=extracted["skills_by_category"],
        total_confirmed=len(extracted["technical_skills"]) + len(extracted["soft_skills"]),
        metadata={
            "sections_analyzed": list(sections.keys()),
            "cleaned_word_count": len(cleaned.split()),
        },
    )
