"""Comprehensive Phase 5 tests for Job Description Analyzer, Semantic Matching, and Skill Gap Engine."""

from pathlib import Path

from fastapi.testclient import TestClient
import pymupdf
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.ml.semantic_matcher import match_target_skill
from app.ml.skill_gap_engine import run_skill_gap_engine
from app.services.job_service import seed_sample_jobs


def _make_pdf_bytes(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    y = 48
    for line in text.split("\n"):
        page.insert_text((48, y), line, fontsize=10)
        y += 14
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture()
def phase5_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_file = tmp_path / "test_phase5.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))

    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Seed the 8 sample job descriptions in the isolated test DB
    seed_db = TestingSessionLocal()
    seed_sample_jobs(seed_db)
    seed_db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    test_engine.dispose()


def _auth_headers(client: TestClient, email: str, name: str = "Maya Chen") -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={"full_name": name, "email": email, "password": "strong-password-123"},
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_seeded_sample_jobs_present_and_labeled(phase5_client: TestClient) -> None:
    resp = phase5_client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 8

    titles = {item["title"] for item in body["items"] if item["is_sample"]}
    expected_titles = {
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "Python Developer",
        "Full Stack Developer",
        "Backend Developer",
        "AI Engineer",
        "Data Engineer",
    }
    assert expected_titles.issubset(titles)

    # Verify GET /api/jobs/{id} returns extracted sections
    sample_id = body["items"][0]["id"]
    detail = phase5_client.get(f"/api/jobs/{sample_id}")
    assert detail.status_code == 200
    extracted = detail.json()["extracted"]
    assert len(extracted["required_skills"]) >= 3
    assert len(extracted["responsibilities"]) >= 2
    assert len(extracted["experience_requirements"]) >= 1
    assert len(extracted["education_requirements"]) >= 1


def test_exact_prompt_example_matched_missing_additional_and_weighted_score() -> None:
    candidate_skills = ["Python", "SQL", "Pandas", "NumPy", "Power BI"]
    required_skills = [
        {"name": "Python", "category": "Programming", "weight": 1.5},
        {"name": "SQL", "category": "Data", "weight": 1.2},
        {"name": "Pandas", "category": "Data", "weight": 1.0},
        {"name": "Machine Learning", "category": "AI/ML", "weight": 1.5},
        {"name": "Natural Language Processing", "category": "AI/ML", "weight": 1.3},
        {"name": "TensorFlow", "category": "AI/ML", "weight": 1.0},
    ]
    preferred_skills = [
        {"name": "Power BI", "category": "Data", "weight": 0.7},
        {"name": "Docker", "category": "Cloud", "weight": 0.7},
    ]

    result = run_skill_gap_engine(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
    )

    matched_req = {s["skill"] for s in result["matched_required_skills"]}
    missing_req = {s["skill"] for s in result["missing_required_skills"]}
    additional = {s["skill"] for s in result["additional_skills"]}

    assert matched_req == {"Python", "SQL", "Pandas"}
    assert missing_req == {"Machine Learning", "Natural Language Processing", "TensorFlow"}
    # Power BI matched preferred, NumPy is additional
    assert "NumPy" in additional

    # Exact weighted formula check: (1.5 + 1.2 + 1.0) / (1.5 + 1.2 + 1.0 + 1.5 + 1.3 + 1.0) * 100 = 3.7 / 7.5 * 100 = 49.33%
    expected_score = round((3.7 / 7.5) * 100.0, 2)
    assert result["compatibility_score"] == expected_score
    assert result["score_explanation"]["matched_required_weight"] == 3.7
    assert result["score_explanation"]["total_required_weight"] == 7.5

    # Preferred score calculated separately: 0.7 / 1.4 * 100 = 50.0%
    assert result["preferred_score"] == 50.0
    assert result["score_explanation"]["preferred_score"] == 50.0


def test_synonym_matching_and_no_false_equivalence() -> None:
    # Synonyms normalize cleanly
    assert match_target_skill("Machine Learning", ["ML"]).match_type == "synonym"
    assert match_target_skill("JavaScript", ["JS"]).match_type == "synonym"
    assert match_target_skill("Natural Language Processing", ["NLP"]).match_type == "synonym"
    assert match_target_skill("Kubernetes", ["K8s"]).match_type == "synonym"

    # Unrelated or distinct canonical skills MUST NOT be treated as equivalent
    assert match_target_skill("Java", ["JavaScript"]).matched is False
    assert match_target_skill("TensorFlow", ["PyTorch"]).matched is False
    assert match_target_skill("AWS", ["Azure"]).matched is False
    assert match_target_skill("Python", ["Docker"]).matched is False
    assert match_target_skill("Kubernetes", ["Power BI"]).matched is False


def test_semantic_matching_for_freeform_skill_phrasing() -> None:
    from app.ml.semantic_matcher import get_active_semantic_model_name

    assert get_active_semantic_model_name() == "sentence-transformers/all-MiniLM-L6-v2"

    # Free-form equivalent phrasing should match via semantic similarity (all-MiniLM-L6-v2)
    outcome = match_target_skill(
        "Machine Learning",
        ["Applied Machine Learning Systems", "Docker"],
    )
    assert outcome.matched is True
    assert outcome.match_type == "semantic"
    assert outcome.similarity >= 0.68

    # Unrelated free-form phrases must NEVER falsely match
    unrelated = match_target_skill("Machine Learning", ["Culinary Arts", "Office Reception"])
    assert unrelated.matched is False


def test_create_custom_job_and_reject_invalid_job_descriptions(phase5_client: TestClient) -> None:
    headers = _auth_headers(phase5_client, "jdcreator@university.edu")

    # 1. Invalid / too-short JD rejected
    bad_short = phase5_client.post(
        "/api/jobs",
        headers=headers,
        json={
            "title": "Engineer",
            "company": "Acme",
            "category": "Software Engineering",
            "raw_text": "Too short",
        },
    )
    assert bad_short.status_code == 422

    # 2. JD with zero recognizable skills rejected
    bad_no_skills = phase5_client.post(
        "/api/jobs",
        headers=headers,
        json={
            "title": "Office Assistant",
            "company": "Acme",
            "category": "Operations",
            "raw_text": "We need someone friendly to answer office phones, welcome lobby visitors, and sort daily mail.",
        },
    )
    assert bad_no_skills.status_code == 422

    # 3. Valid custom JD parsed & persisted
    valid_jd = phase5_client.post(
        "/api/jobs",
        headers=headers,
        json={
            "title": "Senior NLP Engineer",
            "company": "Helios AI",
            "category": "Data & AI",
            "location": "Remote",
            "work_mode": "Remote",
            "raw_text": (
                "Responsibilities\n"
                "- Build production NLP pipelines in Python using PyTorch and FastAPI.\n"
                "Required Qualifications\n"
                "- Strong proficiency in Python, Machine Learning, NLP, PyTorch, and SQL.\n"
                "- 3+ years of experience deploying ML services.\n"
                "- Bachelor's degree in Computer Science.\n"
                "Preferred Qualifications\n"
                "- Experience with Docker, AWS, and React dashboards.\n"
            ),
        },
    )
    assert valid_jd.status_code == 201, valid_jd.text
    job = valid_jd.json()
    assert job["is_sample"] is False
    req_names = {s["name"] for s in job["extracted"]["required_skills"]}
    pref_names = {s["name"] for s in job["extracted"]["preferred_skills"]}
    assert {"Python", "Machine Learning", "Natural Language Processing", "PyTorch", "SQL", "FastAPI"}.issubset(req_names)
    assert {"Docker", "AWS", "React"}.issubset(pref_names)

    # Owner isolation: another user cannot inspect private custom JD
    other_headers = _auth_headers(phase5_client, "other@university.edu", "Other User")
    assert phase5_client.get(f"/api/jobs/{job['id']}", headers=other_headers).status_code == 404


def test_end_to_end_resume_to_skill_gap_and_history_workflow(phase5_client: TestClient) -> None:
    headers = _auth_headers(phase5_client, "workflow@university.edu")

    # Upload a real resume PDF
    resume_text = (
        "Maya Chen\n"
        "Education\n"
        "B.S. Computer Science, MIT 2026\n"
        "Technical Skills\n"
        "Python, SQL, Pandas, NumPy, Power BI\n"
        "Projects\n"
        "Sales Analytics Dashboard\n"
        "- Built Python, Pandas, SQL, and Power BI analytics workflows.\n"
    )
    up = phase5_client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("Maya_Analytics.pdf", _make_pdf_bytes(resume_text), "application/pdf")},
    )
    assert up.status_code == 201, up.text
    resume_id = up.json()["id"]

    # Pick the seeded "Data Scientist" sample job
    jobs = phase5_client.get("/api/jobs", headers=headers).json()["items"]
    ds_job = next(j for j in jobs if j["title"] == "Data Scientist")

    # Run POST /api/analysis/skill-gap using the real uploaded resume_id + job_id
    gap = phase5_client.post(
        "/api/analysis/skill-gap",
        headers=headers,
        json={"resume_id": resume_id, "job_id": ds_job["id"]},
    )
    assert gap.status_code == 201, gap.text
    body = gap.json()

    assert body["resume_id"] == resume_id
    assert body["job_id"] == ds_job["id"]
    assert body["is_sample_job"] is True
    assert 0.0 < body["compatibility_score"] < 100.0
    assert body["jd_semantic_similarity"] > 0.0
    assert len(body["category_breakdown"]) >= 1
    assert len(body["radar_data"]) >= 1

    matched_names = {s["skill"] for s in body["matched_required_skills"]}
    missing_names = {s["skill"] for s in body["missing_required_skills"]}
    assert {"Python", "SQL", "Pandas", "NumPy"}.issubset(matched_names)
    assert "Machine Learning" in missing_names

    # Verify history endpoint persists and lists this analysis
    hist = phase5_client.get("/api/analysis/history", headers=headers)
    assert hist.status_code == 200
    assert hist.json()["total"] == 1
    assert hist.json()["items"][0]["id"] == body["id"]
    assert hist.json()["items"][0]["job_title"] == "Data Scientist"
