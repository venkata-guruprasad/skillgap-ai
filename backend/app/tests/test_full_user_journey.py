"""Phase 8 Complete End-to-End 10-Step User Journey, Security Audit, and Performance Tests."""

from pathlib import Path

import pymupdf
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.ml.career.model_loader import load_trained_bundle
from app.ml.semantic_matcher import load_embedding_model
from app.ml.skill_extractor import get_spacy_nlp
from app.services.job_service import seed_sample_jobs


def _make_pdf_bytes(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture()
def phase8_client(tmp_path: Path):
    db_file = tmp_path / "test_phase8_journey.db"
    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestingSessionLocal() as seed_db:
        seed_sample_jobs(seed_db)

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


def test_complete_10_step_user_journey_and_dashboard_progress(
    phase8_client: TestClient,
) -> None:
    """Exercise the entire 10-step user journey end-to-end across all APIs."""
    # Step 1: Register an account
    reg = phase8_client.post(
        "/api/auth/register",
        json={
            "full_name": "Elena Rostova",
            "email": "elena.journey@university.edu",
            "password": "StrongPassword!2026",
        },
    )
    assert reg.status_code == 201, reg.text
    assert reg.json()["user"]["full_name"] == "Elena Rostova"

    # Step 2: Log in and verify profile + profile update persistence
    login = phase8_client.post(
        "/api/auth/login",
        json={
            "email": "elena.journey@university.edu",
            "password": "StrongPassword!2026",
        },
    )
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    patch_me = phase8_client.patch(
        "/api/auth/me",
        headers=headers,
        json={"full_name": "Elena Rostova-Patel"},
    )
    assert patch_me.status_code == 200
    assert patch_me.json()["full_name"] == "Elena Rostova-Patel"
    assert phase8_client.get("/api/auth/me", headers=headers).json()["full_name"] == "Elena Rostova-Patel"

    # Step 3: Upload a resume (PDF)
    resume_pdf = _make_pdf_bytes(
        "Elena Rostova-Patel\n"
        "elena.journey@university.edu | +1-555-312-9087\n"
        "EDUCATION\n"
        "B.S. Computer Science, State University (2022-2026)\n"
        "TECHNICAL SKILLS\n"
        "Python, SQL, Pandas, NumPy, Scikit-learn, FastAPI, Git, Communication\n"
        "EXPERIENCE\n"
        "Data Science Intern (2025)\n"
        "- Built Python and SQL ETL scripts and Scikit-learn predictive models.\n"
        "PROJECTS\n"
        "- Customer Churn Analyzer using Python, Pandas, and FastAPI.\n"
    )
    upload = phase8_client.post(
        "/api/resume/upload",
        headers=headers,
        files={"file": ("elena_resume.pdf", resume_pdf, "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    resume_body = upload.json()
    resume_id = resume_body["id"]
    extracted_names = [s["name"] for s in resume_body["analysis"]["technical_skills"]]
    assert "Python" in extracted_names
    assert "SQL" in extracted_names

    # Step 4: Extract skills directly via NLP skill extraction endpoint
    extract = phase8_client.post(
        "/api/skills/extract",
        headers=headers,
        json={"text": "Built production APIs in Python, FastAPI, PostgreSQL, and Docker."},
    )
    assert extract.status_code == 200
    ext_names = [s["name"] for s in extract.json()["technical_skills"]]
    assert "Python" in ext_names and "Docker" in ext_names

    # Step 5: Select a seeded job description
    jobs_resp = phase8_client.get("/api/jobs")
    assert jobs_resp.status_code == 200
    jobs = jobs_resp.json()["items"]
    assert len(jobs) >= 8
    ml_job = next(j for j in jobs if j["title"] == "Machine Learning Engineer")

    # Step 6: Analyze skill gaps
    gap = phase8_client.post(
        "/api/analysis/skill-gap",
        headers=headers,
        json={"resume_id": resume_id, "job_id": ml_job["id"]},
    )
    assert gap.status_code == 201, gap.text
    gap_body = gap.json()
    assert gap_body["compatibility_score"] > 0
    assert len(gap_body["missing_required_skills"]) >= 1

    # Step 7: Predict suitable careers (12-role ML engine)
    pred = phase8_client.post(
        "/api/career/predict",
        headers=headers,
        json={"resume_id": resume_id, "career_interests": ["ML", "Data"]},
    )
    assert pred.status_code == 201, pred.text
    pred_body = pred.json()
    assert pred_body["total_roles_evaluated"] == 12
    assert len(pred_body["top_recommendations"]) == 5

    # Step 8: Generate a personalized learning roadmap
    roadmap = phase8_client.post(
        "/api/roadmap/generate",
        headers=headers,
        json={
            "target_role": "Machine Learning Engineer",
            "duration_days": 30,
            "resume_id": resume_id,
            "analysis_id": gap_body["id"],
            "weekly_hours": 10,
            "learning_style": "balanced",
        },
    )
    assert roadmap.status_code == 201, roadmap.text
    rm_body = roadmap.json()
    first_task_id = rm_body["phases"][0]["tasks"][0]["id"]

    # Step 9: Complete a learning task
    complete = phase8_client.patch(
        f"/api/roadmap/tasks/{first_task_id}",
        headers=headers,
        json={"is_completed": True},
    )
    assert complete.status_code == 200
    assert complete.json()["task"]["is_completed"] is True
    assert complete.json()["roadmap_progress"]["completed_tasks"] == 1

    # Step 10: Verify live dashboard analytics reflects the entire journey & task completion!
    dash = phase8_client.get("/api/dashboard/analytics", headers=headers)
    assert dash.status_code == 200, dash.text
    dash_body = dash.json()
    assert dash_body["counts"]["resumes"] == 1
    assert dash_body["counts"]["analyses"] == 1
    assert dash_body["counts"]["career_predictions"] == 1
    assert dash_body["counts"]["roadmaps"] == 1
    assert dash_body["latest_resume"]["file_name"] == "elena_resume.pdf"
    assert len(dash_body["latest_career_recommendations"]) == 5
    assert dash_body["active_roadmap"]["completed_tasks"] == 1
    assert dash_body["active_roadmap"]["progress_percent"] > 0
    assert len(dash_body["recent_activity"]) >= 4


def test_security_audit_headers_sqli_safety_and_user_isolation(
    phase8_client: TestClient,
) -> None:
    """Verify security headers, SQLi parameterization safety, and strict cross-user isolation."""
    # Security headers present on responses
    health = phase8_client.get("/api/health")
    assert health.status_code == 200
    assert health.headers.get("x-content-type-options") == "nosniff"
    assert health.headers.get("x-frame-options") == "DENY"
    assert health.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    # SQL injection payload on login & job search must not error or bypass auth
    sqli_login = phase8_client.post(
        "/api/auth/login",
        json={"email": "' OR '1'='1' --", "password": "' OR '1'='1"},
    )
    assert sqli_login.status_code == 401

    sqli_jobs = phase8_client.get("/api/jobs", params={"search": "'; DROP TABLE users; --"})
    assert sqli_jobs.status_code == 200

    # Dashboard analytics requires authentication
    assert phase8_client.get("/api/dashboard/analytics").status_code == 401
    assert phase8_client.patch("/api/auth/me", json={"full_name": "Anon"}).status_code == 401

    # User A creates data; User B's dashboard must see zero items from User A
    reg_a = phase8_client.post(
        "/api/auth/register",
        json={"full_name": "Alice Security", "email": "alice@sec.edu", "password": "Password123!"},
    )
    headers_a = {"Authorization": f"Bearer {reg_a.json()['access_token']}"}
    phase8_client.post(
        "/api/roadmap/generate",
        headers=headers_a,
        json={"target_role": "Data Analyst", "duration_days": 30, "resume_skills": ["SQL"]},
    )

    reg_b = phase8_client.post(
        "/api/auth/register",
        json={"full_name": "Bob Isolated", "email": "bob@sec.edu", "password": "Password123!"},
    )
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    dash_b = phase8_client.get("/api/dashboard/analytics", headers=headers_b)
    assert dash_b.status_code == 200
    assert dash_b.json()["counts"] == {
        "resumes": 0,
        "analyses": 0,
        "career_predictions": 0,
        "roadmaps": 0,
    }
    assert dash_b.json()["active_roadmap"] is None


def test_ml_models_are_cached_singletons_not_reloaded_per_request() -> None:
    """Confirm spaCy, SentenceTransformer, and Career ML bundle are cached in memory."""
    nlp1 = get_spacy_nlp()
    nlp2 = get_spacy_nlp()
    assert nlp1 is nlp2

    emb1, name1 = load_embedding_model()
    emb2, name2 = load_embedding_model()
    assert emb1 is emb2
    assert name1 == name2

    bundle1 = load_trained_bundle()
    bundle2 = load_trained_bundle()
    assert bundle1 is bundle2


def test_production_config_guards_and_managed_postgres_url_normalization() -> None:
    """Verify production config blocks weak secrets, debug mode, wildcard CORS, and SQLite."""
    from app.config import Settings, normalize_database_url

    assert (
        normalize_database_url("postgres://u:p@ep-demo.neon.tech/skillgap?sslmode=require")
        == "postgresql+psycopg2://u:p@ep-demo.neon.tech/skillgap?sslmode=require"
    )
    assert (
        normalize_database_url("postgresql://u:p@db.supabase.co:5432/postgres?sslmode=require")
        == "postgresql+psycopg2://u:p@db.supabase.co:5432/postgres?sslmode=require"
    )

    valid_prod = Settings(
        _env_file=None,
        APP_ENV="production",
        DEBUG=True,  # Must be forced False in production
        SECRET_KEY="a" * 48,
        DATABASE_URL="postgres://user:pass@ep-demo.neon.tech/skillgap?sslmode=require",
        CORS_ORIGINS="https://skillgap-ai.vercel.app",
    )
    assert valid_prod.is_production is True
    assert valid_prod.effective_debug is False
    assert valid_prod.is_postgres_configured is True
    valid_prod.validate_production_config()

    # Placeholder/short secret rejected in production
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        Settings(
            _env_file=None,
            APP_ENV="production",
            SECRET_KEY="replace_with_a_secure_random_secret_key_at_least_32_chars",
            DATABASE_URL="postgresql://u:p@host/db",
            CORS_ORIGINS="https://skillgap-ai.vercel.app",
        ).validate_production_config()

    # Wildcard CORS rejected in production
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        Settings(
            _env_file=None,
            APP_ENV="production",
            SECRET_KEY="x" * 48,
            DATABASE_URL="postgresql://u:p@host/db",
            CORS_ORIGINS="*",
        ).validate_production_config()

    # Missing PostgreSQL rejected in production (SQLite fallback disabled)
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        Settings(
            _env_file=None,
            APP_ENV="production",
            SECRET_KEY="x" * 48,
            DATABASE_URL=None,
            POSTGRES_HOST="",
            CORS_ORIGINS="https://skillgap-ai.vercel.app",
        ).validate_production_config()
