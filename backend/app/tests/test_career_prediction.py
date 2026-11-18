"""Comprehensive Phase 6 tests for the ML Career Prediction Engine, Evaluation, and APIs."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.ml.career.dataset_builder import CAREER_ROLE_CATALOG
from app.ml.career.model_loader import load_trained_bundle
from app.ml.career.model_store import EVALUATION_REPORT_PATH, MODEL_BUNDLE_PATH
from app.services.job_service import seed_sample_jobs

EXPECTED_12_ROLES = {
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Python Developer",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "AI Engineer",
    "Business Analyst",
    "Data Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
}


@pytest.fixture()
def phase6_client(tmp_path: Path):
    db_file = tmp_path / "test_phase6.db"
    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

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


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={"full_name": "Elena Park", "email": email, "password": "strong-password-123"},
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_all_12_career_roles_supported_and_model_artifacts_saved() -> None:
    catalog_titles = {r["title"] for r in CAREER_ROLE_CATALOG}
    assert catalog_titles == EXPECTED_12_ROLES

    bundle = load_trained_bundle()
    assert MODEL_BUNDLE_PATH.exists()
    assert EVALUATION_REPORT_PATH.exists()
    assert set(bundle["classes"]) == EXPECTED_12_ROLES
    assert bundle["is_synthetic_dataset"] is True

    eval_report = bundle["evaluation_report"]
    assert 0.0 < eval_report["accuracy"] <= 1.0
    assert 0.0 < eval_report["precision_macro"] <= 1.0
    assert 0.0 < eval_report["recall_macro"] <= 1.0
    assert 0.0 < eval_report["f1_macro"] <= 1.0
    assert len(eval_report["confusion_matrix"]) == 12
    assert len(eval_report["confusion_matrix"][0]) == 12
    assert len(eval_report["model_comparison"]) == 3
    assert eval_report["train_samples"] > eval_report["test_samples"] > 0


def test_career_predict_endpoint_returns_top_5_with_accurate_domain_ranking(
    phase6_client: TestClient,
) -> None:
    headers = _auth_headers(phase6_client, "mlstudent@university.edu")

    # 1. Data & AI profile should rank Data Scientist / ML Engineer / AI Engineer at the top
    resp_ai = phase6_client.post(
        "/api/career/predict",
        headers=headers,
        json={
            "resume_skills": [
                "Python",
                "SQL",
                "Pandas",
                "NumPy",
                "Machine Learning",
                "Natural Language Processing",
                "PyTorch",
                "FastAPI",
            ],
            "education": ["Master of Science in Data Science"],
            "experience": ["Built NLP classification and Machine Learning models in Python."],
            "projects": ["Semantic Resume Analyzer using PyTorch, NLP, and FastAPI."],
            "career_interests": ["AI", "Machine Learning"],
        },
    )
    assert resp_ai.status_code == 201, resp_ai.text
    body = resp_ai.json()

    assert body["total_roles_evaluated"] == 12
    assert len(body["top_recommendations"]) == 5
    assert "not actual employment" in body["disclaimer"].lower()

    top_3_titles = {r["career_title"] for r in body["top_recommendations"][:3]}
    assert top_3_titles.intersection({"AI Engineer", "Data Scientist", "Machine Learning Engineer"})

    for rec in body["top_recommendations"]:
        assert 0.0 <= rec["compatibility_score"] <= 100.0
        assert isinstance(rec["matching_skills"], list)
        assert isinstance(rec["missing_skills"], list)
        assert isinstance(rec["required_additional_skills"], list)
        assert len(rec["explanation"]) > 20

    # Verify GET /api/career/recommendations returns the persisted top-5 prediction
    saved = phase6_client.get("/api/career/recommendations", headers=headers)
    assert saved.status_code == 200
    assert saved.json()["prediction_id"] == body["prediction_id"]
    assert len(saved.json()["top_recommendations"]) == 5


def test_career_predict_distinguishes_cybersecurity_and_frontend_profiles(
    phase6_client: TestClient,
) -> None:
    headers = _auth_headers(phase6_client, "secstudent@university.edu")

    # Cybersecurity profile should rank Cybersecurity Analyst #1
    resp_sec = phase6_client.post(
        "/api/career/predict",
        headers=headers,
        json={
            "resume_skills": ["Cybersecurity", "SIEM", "Network Security", "Linux", "Python"],
            "education": ["B.S. in Cybersecurity"],
            "experience": ["SOC Analyst intern monitoring Splunk SIEM alerts and firewalls."],
            "projects": ["Automated vulnerability assessment and Wireshark packet analyzer."],
            "career_interests": ["Cybersecurity"],
        },
    )
    assert resp_sec.status_code == 201
    assert resp_sec.json()["top_recommendations"][0]["career_title"] == "Cybersecurity Analyst"

    # Frontend profile should rank Frontend Developer or Full Stack Developer #1
    resp_fe = phase6_client.post(
        "/api/career/predict",
        headers=headers,
        json={
            "resume_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Git"],
            "education": ["B.S. in Computer Science"],
            "experience": ["Frontend engineering intern building responsive React TypeScript SPAs."],
            "projects": ["Accessible SaaS UI design system with Tailwind CSS and React."],
            "career_interests": ["Frontend"],
        },
    )
    assert resp_fe.status_code == 201
    assert resp_fe.json()["top_recommendations"][0]["career_title"] in {
        "Frontend Developer",
        "Full Stack Developer",
    }


def test_career_predict_validation_and_auth_enforced(phase6_client: TestClient) -> None:
    assert phase6_client.get("/api/career/recommendations").status_code == 401
    assert phase6_client.post("/api/career/predict", json={"resume_skills": ["Python"]}).status_code == 401

    headers = _auth_headers(phase6_client, "emptyprofile@university.edu")
    bad = phase6_client.post("/api/career/predict", headers=headers, json={})
    assert bad.status_code == 422
