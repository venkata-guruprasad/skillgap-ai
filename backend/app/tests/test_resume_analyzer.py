"""Comprehensive Phase 4 test suite for Resume Upload, NLP Extraction, and Skill Taxonomy."""

from io import BytesIO
from pathlib import Path
import struct
import zlib

import docx
from fastapi.testclient import TestClient
import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app


def _make_pdf_bytes(text: str) -> bytes:
    """Create a real multi-line PDF in memory using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    y = 50
    for line in text.split("\n"):
        if y > 780:
            page = doc.new_page()
            y = 50
        page.insert_text((50, y), line, fontsize=10)
        y += 14
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _make_scanned_image_pdf_bytes() -> bytes:
    """Create a valid PDF containing an embedded PNG image with zero selectable text."""
    # Build a minimal valid 2x2 RGB PNG in memory
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    raw_pixels = b"\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00\xff"
    ihdr = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw_pixels))
        + _chunk(b"IEND", b"")
    )

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_image(pymupdf.Rect(50, 50, 200, 200), stream=png_bytes)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _make_docx_bytes(lines: list[str], table_rows: list[list[str]] | None = None) -> bytes:
    """Create a real DOCX document in memory using python-docx."""
    document = docx.Document()
    for line in lines:
        document.add_paragraph(line)
    if table_rows:
        table = document.add_table(rows=len(table_rows), cols=len(table_rows[0]))
        for r_idx, row in enumerate(table_rows):
            for c_idx, val in enumerate(row):
                table.cell(r_idx, c_idx).text = val
    buf = BytesIO()
    document.save(buf)
    return buf.getvalue()


@pytest.fixture()
def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Isolated SQLite database and upload directory per test module."""
    db_file = tmp_path / "test_phase4.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))

    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, upload_dir
    app.dependency_overrides.clear()
    test_engine.dispose()


def _register_and_get_headers(client: TestClient, email: str, name: str = "Jordan Lee") -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={"full_name": name, "email": email, "password": "secure-password-123"},
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_authentication_required_for_resume_endpoints(test_client) -> None:
    client, _ = test_client
    assert client.get("/api/resume/history").status_code == 401
    assert (
        client.post(
            "/api/skills/extract",
            json={"text": "Technical Skills: Python, React, Docker"},
        ).status_code
        == 401
    )


def test_valid_pdf_upload_nlp_extraction_and_privacy(test_client) -> None:
    client, upload_dir = test_client
    headers = _register_and_get_headers(client, "alice@university.edu", "Alice Morgan")

    resume_text = """
Alice Morgan
alice.morgan@example.com | (415) 555-8291

Education
Bachelor of Science in Computer Science
Stanford University | 2022 - 2026

Technical Skills
Programming: Python, JS, C++
Data: SQL, Pandas, NumPy, Power BI
AI/ML: ML, Deep Learning, NLP, PyTorch
Web: React, FastAPI, HTML, CSS
Cloud: AWS, Docker, K8s

Work Experience
Software Engineering Intern | CloudScale Inc | May 2025 - Aug 2025
- Built scalable FastAPI microservices in Python deployed on AWS with Docker and Kubernetes.
- Collaborated with cross-functional teams using Agile and Scrum practices to improve API latency by 35%.

Projects
Smart Resume Analyzer
- Engineered an NLP and ML pipeline using Python, React, and PyTorch for semantic skill matching.

Certifications
AWS Certified Cloud Practitioner
"""
    pdf_bytes = _make_pdf_bytes(resume_text)
    resp = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("Alice_Morgan_Resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()

    assert body["file_name"] == "Alice_Morgan_Resume.pdf"
    assert body["file_type"] == "PDF"
    assert body["extraction_status"] == "completed"

    analysis = body["analysis"]
    # PII must be redacted, not exposed raw
    assert analysis["personal_info"]["pii_redacted"] is True
    assert analysis["personal_info"]["email_detected"] is True
    assert analysis["personal_info"]["masked_email"] == "a***@example.com"
    assert "alice.morgan@example.com" not in str(analysis)
    assert "555-8291" not in str(analysis)

    # Synonym normalization & categories verified
    tech_names = {s["name"] for s in analysis["technical_skills"]}
    assert "Python" in tech_names
    assert "JavaScript" in tech_names  # normalized from JS
    assert "Machine Learning" in tech_names  # normalized from ML
    assert "Natural Language Processing" in tech_names  # normalized from NLP
    assert "Kubernetes" in tech_names  # normalized from K8s
    assert "React" in tech_names
    assert "FastAPI" in tech_names
    assert "AWS" in tech_names
    assert "Docker" in tech_names
    assert "Power BI" in tech_names

    # Evidence snippets present
    for skill in analysis["technical_skills"]:
        assert skill["confirmed"] is True
        assert len(skill["evidence"]) >= 1

    # Structured sections extracted from content
    assert len(analysis["education"]) >= 1
    assert len(analysis["experience"]) >= 1
    assert len(analysis["projects"]) >= 1
    assert len(analysis["certifications"]) >= 1
    assert len(analysis["soft_skills"]) >= 1

    # Verify history, detail, owner isolation, and delete
    resume_id = body["id"]
    hist = client.get("/api/resume/history", headers=headers)
    assert hist.status_code == 200
    assert hist.json()["total"] == 1
    assert hist.json()["items"][0]["id"] == resume_id

    detail = client.get(f"/api/resume/{resume_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == resume_id

    # Owner isolation: another user cannot access or delete Alice's resume
    other_headers = _register_and_get_headers(client, "bob@university.edu", "Bob Smith")
    assert client.get(f"/api/resume/{resume_id}", headers=other_headers).status_code == 404
    assert client.delete(f"/api/resume/{resume_id}", headers=other_headers).status_code == 404

    # Delete removes DB record and file from disk
    stored_files_before = list(upload_dir.rglob("*Alice_Morgan_Resume.pdf"))
    assert len(stored_files_before) == 1
    deleted = client.delete(f"/api/resume/{resume_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["deleted_id"] == resume_id
    assert len(list(upload_dir.rglob("*Alice_Morgan_Resume.pdf"))) == 0


def test_valid_docx_upload_reflects_uploaded_content(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "docxuser@university.edu", "Priya Patel")

    docx_bytes = _make_docx_bytes(
        lines=[
            "Priya Patel",
            "Education",
            "Master of Science in Data Analytics, Georgia Tech (2024 - 2026)",
            "Technical Skills",
            "Data & Cloud: SQL, Tableau, Microsoft Excel, Azure, Pandas, TensorFlow",
            "Work Experience",
            "Data Analyst Intern | InsightCorp | 2025",
            "- Built executive Tableau dashboards and automated SQL reporting workflows.",
            "- Led stakeholder communication and technical writing across analytics teams.",
            "Projects",
            "Customer Churn Prediction",
            "- Developed TensorFlow and Pandas churn pipelines deployed on Microsoft Azure.",
        ]
    )

    resp = client.post(
        "/api/resume/upload",
        headers=headers,
        files={
            "file": (
                "Priya_Analytics.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert resp.status_code == 201, resp.text
    analysis = resp.json()["analysis"]
    tech_names = {s["name"] for s in analysis["technical_skills"]}

    assert "SQL" in tech_names
    assert "Tableau" in tech_names
    assert "Excel" in tech_names
    assert "Azure" in tech_names
    assert "Pandas" in tech_names
    assert "TensorFlow" in tech_names
    # Ensure skills NOT in the uploaded DOCX are NOT fabricated
    assert "React" not in tech_names
    assert "Kubernetes" not in tech_names


def test_invalid_file_type_rejected(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "invalid@university.edu")

    resp = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("notes.txt", b"Python Java React Docker AWS", "text/plain")},
    )
    assert resp.status_code == 400
    assert "Only PDF" in resp.json()["detail"]


def test_empty_resume_rejected(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "empty@university.edu")

    # 1. Zero-byte file
    r1 = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert r1.status_code == 422

    # 2. Valid PDF structure with blank text
    blank_pdf = _make_pdf_bytes("   \n   ")
    r2 = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("blank.pdf", blank_pdf, "application/pdf")},
    )
    assert r2.status_code == 422
    assert "no readable text" in r2.json()["detail"].lower()


def test_large_file_exceeding_5mb_rejected(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "large@university.edu")

    oversized = b"%PDF-1.4\n" + (b"A" * (5 * 1024 * 1024 + 128))
    resp = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("huge_resume.pdf", oversized, "application/pdf")},
    )
    assert resp.status_code == 413
    assert "5 MB" in resp.json()["detail"]


def test_duplicate_upload_detected(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "dup@university.edu")

    pdf_bytes = _make_pdf_bytes(
        "Samira Khan\nTechnical Skills\nPython, FastAPI, Docker, SQL, AWS\nEducation\nB.Tech Computer Science 2025"
    )
    first = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("Samira_Resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert first.status_code == 201
    first_id = first.json()["id"]

    second = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("Samira_Resume_Copy.pdf", pdf_bytes, "application/pdf")},
    )
    assert second.status_code == 409
    assert second.json()["detail"]["existing_resume_id"] == first_id


def test_malformed_and_scanned_documents_handled_gracefully(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "malformed@university.edu")

    # Corrupted PDF bytes
    bad_pdf = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("corrupt.pdf", b"not-a-real-pdf-header-at-all", "application/pdf")},
    )
    assert bad_pdf.status_code == 422

    # Corrupted DOCX bytes
    bad_docx = client.post(
        "/api/resume/upload",
        headers=headers,
        files={
            "file": (
                "corrupt.docx",
                b"PK\x03\x04corrupted-zip-content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert bad_docx.status_code == 422

    # Scanned image-only PDF
    scanned_pdf = _make_scanned_image_pdf_bytes()
    scanned_resp = client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("scanned_cv.pdf", scanned_pdf, "application/pdf")},
    )
    assert scanned_resp.status_code == 422
    assert "scanned" in scanned_resp.json()["detail"].lower()


def test_skill_extraction_endpoint_avoids_false_positives_and_normalizes_synonyms(test_client) -> None:
    client, _ = test_client
    headers = _register_and_get_headers(client, "nlp@university.edu")

    # Weak/unrelated prose should NOT confirm Excel, Machine Learning, React, or Go
    unrelated = client.post(
        "/api/skills/extract",
        headers=headers,
        json={
            "text": (
                "I strive to excel at culinary arts, measure 500 ml of water carefully, "
                "react quickly to customer inquiries, and always go above and beyond."
            )
        },
    )
    assert unrelated.status_code == 200
    unrelated_confirmed = {s["name"] for s in unrelated.json()["technical_skills"]}
    assert "Excel" not in unrelated_confirmed
    assert "Machine Learning" not in unrelated_confirmed
    assert "React" not in unrelated_confirmed
    assert "Go" not in unrelated_confirmed

    # Mixed sentence: valid ML skill AND '500 ml' / 'excel at' on the same line
    mixed = client.post(
        "/api/skills/extract",
        headers=headers,
        json={
            "text": (
                "Technical Skills: Python, ML, JS, NLP, Docker, AWS. "
                "I also excel at cooking and drink 500 ml of water."
            )
        },
    )
    assert mixed.status_code == 200
    mixed_names = {s["name"] for s in mixed.json()["technical_skills"]}
    assert {"Python", "Machine Learning", "JavaScript", "Natural Language Processing", "Docker", "AWS"}.issubset(mixed_names)
    assert "Excel" not in mixed_names

    # Real technical text with synonyms confirms normalized canonical names + evidence
    technical = client.post(
        "/api/skills/extract",
        headers=headers,
        json={
            "text": (
                "Technical Skills: Python, JS, ML, NLP, Node.js, React, FastAPI, SQL, Docker, AWS\n"
                "Projects: Built a deep learning NLP model with TensorFlow and deployed via Docker."
            )
        },
    )
    assert technical.status_code == 200
    payload = technical.json()
    confirmed_names = {s["name"] for s in payload["technical_skills"]}
    assert {
        "Python",
        "JavaScript",
        "Machine Learning",
        "Natural Language Processing",
        "Node.js",
        "React",
        "FastAPI",
        "SQL",
        "Docker",
        "AWS",
        "Deep Learning",
        "TensorFlow",
    }.issubset(confirmed_names)
    assert all(len(s["evidence"]) >= 1 for s in payload["technical_skills"])
