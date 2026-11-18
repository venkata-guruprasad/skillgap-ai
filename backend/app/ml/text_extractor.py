"""Resume text extraction for PDF (PyMuPDF) and DOCX (python-docx)."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable, Optional
import zipfile

import docx
import pymupdf

PDF_MAGIC = b"%PDF-"
ZIP_MAGIC = b"PK\x03\x04"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",  # fallback sent by some browsers/clients; verified by magic bytes
}

# Optional OCR callback hook: Callable[[bytes], str]
OcrExtractorHook = Callable[[bytes], str]


class ResumeExtractionError(Exception):
    """Base error raised during resume validation or text extraction."""


class UnsupportedFileTypeError(ResumeExtractionError):
    """Raised when the uploaded file is not a valid PDF or DOCX."""


class MalformedDocumentError(ResumeExtractionError):
    """Raised when a PDF or DOCX file is corrupted or unreadable."""


class ScannedDocumentError(ResumeExtractionError):
    """Raised when a PDF contains image-only pages without selectable text."""


class EmptyResumeError(ResumeExtractionError):
    """Raised when extracted and cleaned resume text is empty or too short."""


@dataclass
class ExtractionResult:
    raw_text: str
    file_type: str
    page_count: int
    used_ocr: bool = False


def validate_file_type_and_signature(
    filename: str,
    file_bytes: bytes,
    content_type: Optional[str] = None,
) -> str:
    """Validate extension, MIME type, and file magic bytes. Returns normalized type ('pdf'|'docx')."""
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            "Unsupported file type. Only PDF (.pdf) and DOCX (.docx) files are accepted."
        )

    if content_type and content_type.lower() not in ALLOWED_CONTENT_TYPES:
        # Allow minor browser variants only if magic bytes match below
        if "pdf" not in content_type.lower() and "word" not in content_type.lower() and "officedocument" not in content_type.lower():
            raise UnsupportedFileTypeError(
                f"Unsupported MIME type '{content_type}'. Upload a valid PDF or DOCX resume."
            )

    if not file_bytes or len(file_bytes) < 8:
        raise MalformedDocumentError(
            "The uploaded file is empty or truncated and cannot be read."
        )

    if ext == ".pdf":
        # PDF magic header must appear within the first 1024 bytes per PDF spec
        if PDF_MAGIC not in file_bytes[:1024]:
            raise MalformedDocumentError(
                "Invalid PDF signature. The file appears corrupted or is not a real PDF document."
            )
        return "pdf"

    # DOCX is a ZIP container that must include word/document.xml
    if not file_bytes.startswith(ZIP_MAGIC):
        raise MalformedDocumentError(
            "Invalid DOCX signature. The file appears corrupted or is not a real Word document."
        )
    try:
        with zipfile.ZipFile(BytesIO(file_bytes)) as zf:
            if "word/document.xml" not in zf.namelist():
                raise MalformedDocumentError(
                    "Invalid DOCX archive structure (missing word/document.xml)."
                )
    except zipfile.BadZipFile as exc:
        raise MalformedDocumentError(
            "Corrupted DOCX archive. Please re-save the document and try again."
        ) from exc

    return "docx"


def extract_text_from_pdf(
    file_bytes: bytes,
    ocr_hook: Optional[OcrExtractorHook] = None,
) -> ExtractionResult:
    """Extract text from a PDF using PyMuPDF, with graceful scanned-PDF detection & OCR hook."""
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise MalformedDocumentError(
            f"Unable to open PDF document: the file may be corrupted or encrypted ({exc})."
        ) from exc

    try:
        if doc.needs_pass:
            raise MalformedDocumentError(
                "Password-protected PDFs are not supported. Please upload an unlocked PDF."
            )

        page_count = len(doc)
        if page_count == 0:
            raise EmptyResumeError("The uploaded PDF contains zero pages.")

        page_texts = []
        image_count = 0
        for page in doc:
            text = page.get_text("text") or ""
            page_texts.append(text)
            image_count += len(page.get_images(full=False))

        combined = "\n".join(page_texts).strip()
        alnum_chars = sum(1 for ch in combined if ch.isalnum())

        if alnum_chars < 25:
            if image_count > 0:
                if ocr_hook is not None:
                    ocr_text = (ocr_hook(file_bytes) or "").strip()
                    if sum(1 for ch in ocr_text if ch.isalnum()) >= 25:
                        return ExtractionResult(
                            raw_text=ocr_text,
                            file_type="pdf",
                            page_count=page_count,
                            used_ocr=True,
                        )
                raise ScannedDocumentError(
                    "This PDF appears to be a scanned or image-only document with no "
                    "selectable text. Please export a text-based PDF/DOCX resume, or "
                    "enable an OCR provider via the OCR integration hook."
                )
            raise EmptyResumeError(
                "The uploaded PDF contains no readable text content."
            )

        return ExtractionResult(
            raw_text=combined,
            file_type="pdf",
            page_count=page_count,
            used_ocr=False,
        )
    finally:
        doc.close()


def extract_text_from_docx(file_bytes: bytes) -> ExtractionResult:
    """Extract text from paragraphs, tables, and headers/footers in a DOCX file."""
    try:
        document = docx.Document(BytesIO(file_bytes))
    except Exception as exc:
        raise MalformedDocumentError(
            f"Unable to parse DOCX document: file appears malformed ({exc})."
        ) from exc

    chunks = []

    # Headers (some resumes put Name / Contact info in header)
    for section in document.sections:
        for para in section.header.paragraphs:
            if para.text and para.text.strip():
                chunks.append(para.text.strip())

    # Main body paragraphs
    for para in document.paragraphs:
        if para.text and para.text.strip():
            chunks.append(para.text.strip())

    # Tables (common in two-column resume templates)
    for table in document.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text and cell.text.strip()]
            if row_cells:
                # Deduplicate merged cells that repeat identical text across a row
                deduped_cells = list(dict.fromkeys(row_cells))
                chunks.append(" | ".join(deduped_cells))

    combined = "\n".join(chunks).strip()
    if sum(1 for ch in combined if ch.isalnum()) < 20:
        raise EmptyResumeError(
            "The uploaded DOCX document is empty or contains insufficient readable text."
        )

    return ExtractionResult(
        raw_text=combined,
        file_type="docx",
        page_count=max(1, len(document.sections)),
        used_ocr=False,
    )


def extract_resume_text(
    filename: str,
    file_bytes: bytes,
    content_type: Optional[str] = None,
    ocr_hook: Optional[OcrExtractorHook] = None,
) -> ExtractionResult:
    """Validate and extract raw text from a PDF or DOCX resume."""
    file_type = validate_file_type_and_signature(filename, file_bytes, content_type)
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes, ocr_hook=ocr_hook)
    return extract_text_from_docx(file_bytes)
