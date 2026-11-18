"""Comprehensive Phase 7 tests for Personalized AI Learning Roadmap Generator & Progress Persistence."""

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.ml.roadmap.llm_client import VerifiedResourceSchema
from app.ml.roadmap.resource_catalog import SKILL_CURRICULUM_CATALOG, is_trusted_resource_url


@pytest.fixture()
def phase7_client(tmp_path: Path):
    db_file = tmp_path / "test_phase7.db"
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
        yield client
    app.dependency_overrides.clear()
    test_engine.dispose()


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    resp = client.post(
        "/api/auth/register",
        json={"full_name": "Nadia Okafor", "email": email, "password": "strong-password-123"},
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_all_catalog_resource_urls_are_verified_trusted_domains() -> None:
    for skill, entry in SKILL_CURRICULUM_CATALOG.items():
        assert len(entry["resources"]) >= 1, f"Missing resources for {skill}"
        for res in entry["resources"]:
            assert is_trusted_resource_url(res["url"]), f"Untrusted URL for {skill}: {res['url']}"

    # Pydantic validator rejects untrusted/fabricated domains
    with pytest.raises(ValidationError):
        VerifiedResourceSchema(
            title="Fake Course",
            source="Unknown",
            url="https://fake-unverified-domain.example.com/course",
        )


def test_generate_30_60_90_day_roadmaps_and_persist_task_progress(
    phase7_client: TestClient,
) -> None:
    headers = _auth_headers(phase7_client, "roadmap@university.edu")

    # 1. Generate a 30-day roadmap deterministically (no LLM key needed)
    gen30 = phase7_client.post(
        "/api/roadmap/generate",
        headers=headers,
        json={
            "target_role": "Machine Learning Engineer",
            "duration_days": 30,
            "resume_skills": ["Python", "SQL", "Pandas"],
            "missing_skills": ["Machine Learning", "PyTorch", "Docker"],
            "weekly_hours": 12,
            "learning_style": "project-heavy",
        },
    )
    assert gen30.status_code == 201, gen30.text
    rm30 = gen30.json()

    assert rm30["duration_days"] == 30
    assert rm30["estimated_weeks"] == 4
    assert rm30["generation_mode"] == "deterministic"
    assert rm30["target_role"] == "Machine Learning Engineer"
    assert rm30["progress"]["completed_tasks"] == 0
    assert rm30["progress"]["total_tasks"] >= 9
    assert len(rm30["phases"]) == 3

    # Verify required structure on every learning phase
    for phase in rm30["phases"]:
        assert phase["skill_name"]
        assert len(phase["learning_objectives"]) >= 1
        assert len(phase["practical_exercises"]) >= 1
        assert phase["mini_project"]
        assert phase["assessment_checkpoint"]
        assert phase["estimated_hours"] > 0
        assert len(phase["resources"]) >= 1
        assert len(phase["tasks"]) >= 4
        for res in phase["resources"]:
            assert is_trusted_resource_url(res["url"])

    # 2. Mark all tasks in Phase 1 complete via PATCH /api/roadmap/tasks/{id}
    phase1_tasks = rm30["phases"][0]["tasks"]
    for t in phase1_tasks:
        patch_resp = phase7_client.patch(
            f"/api/roadmap/tasks/{t['id']}",
            headers=headers,
            json={"is_completed": True},
        )
        assert patch_resp.status_code == 200, patch_resp.text
        assert patch_resp.json()["task"]["is_completed"] is True
        assert patch_resp.json()["task"]["completed_at"] is not None

    # 3. Reload roadmap via GET /api/roadmap/{id} -> verify persistence & milestone completion!
    reloaded = phase7_client.get(f"/api/roadmap/{rm30['id']}", headers=headers)
    assert reloaded.status_code == 200
    rel_body = reloaded.json()
    assert rel_body["progress"]["completed_tasks"] == len(phase1_tasks)
    assert rel_body["progress"]["completed_milestones"] == 1
    assert rel_body["phases"][0]["is_completed"] is True

    # 4. Regenerate 60-day and 90-day plans -> verify history via GET /api/roadmap
    gen60 = phase7_client.post(
        "/api/roadmap/generate",
        headers=headers,
        json={"target_role": "Full Stack Developer", "duration_days": 60, "resume_skills": ["Python"]},
    )
    assert gen60.status_code == 201
    assert gen60.json()["duration_days"] == 60
    assert gen60.json()["estimated_weeks"] == 8

    gen90 = phase7_client.post(
        "/api/roadmap/generate",
        headers=headers,
        json={"target_role": "Cloud Engineer", "duration_days": 90, "resume_skills": ["Linux"]},
    )
    assert gen90.status_code == 201
    assert gen90.json()["duration_days"] == 90
    assert gen90.json()["estimated_weeks"] == 12

    hist = phase7_client.get("/api/roadmap", headers=headers)
    assert hist.status_code == 200
    assert hist.json()["total"] == 3
    assert hist.json()["active_roadmap_id"] == gen90.json()["id"]

    # 5. Cross-user owner isolation enforced
    other_headers = _auth_headers(phase7_client, "intruder@university.edu")
    assert phase7_client.get(f"/api/roadmap/{rm30['id']}", headers=other_headers).status_code == 404
    assert (
        phase7_client.patch(
            f"/api/roadmap/tasks/{phase1_tasks[0]['id']}",
            headers=other_headers,
            json={"is_completed": False},
        ).status_code
        == 404
    )


def test_roadmap_endpoints_require_authentication(phase7_client: TestClient) -> None:
    assert phase7_client.get("/api/roadmap").status_code == 401
    assert (
        phase7_client.post(
            "/api/roadmap/generate",
            json={"target_role": "Data Scientist", "duration_days": 30},
        ).status_code
        == 401
    )


def test_llm_sanitization_replaces_untrusted_links_and_validates_schema() -> None:
    from app.ml.roadmap.llm_client import (
        GeneratedRoadmapPlan,
        _sanitize_resources_for_phases,
        is_llm_configured,
    )

    assert is_llm_configured() is False

    raw_llm_output = {
        "title": "30-Day Python Developer Learning Roadmap",
        "target_role": "Python Developer",
        "duration_days": 30,
        "estimated_weeks": 4,
        "summary_explanation": "Personalized 30-day plan focusing on FastAPI and Docker.",
        "prioritized_missing_skills": ["FastAPI", "Docker"],
        "phases": [
            {
                "phase_number": 1,
                "timeframe": "Days 1-15 (Week 1-2)",
                "title": "Phase 1: FastAPI Mastery",
                "skill_name": "FastAPI",
                "priority": "Critical",
                "estimated_hours": 14,
                "learning_objectives": ["Build typed REST APIs with Pydantic validation."],
                "weekly_tasks": [
                    {
                        "week_label": "Week 1",
                        "title": "Implement FastAPI routers and dependency injection",
                        "description": "Use SQLAlchemy sessions and Pydantic schemas.",
                        "task_type": "study",
                        "estimated_hours": 6,
                    }
                ],
                "practical_exercises": ["Build a CRUD API with pytest coverage."],
                "mini_project": "Create an authenticated task tracker API with FastAPI.",
                "assessment_checkpoint": "Pass pytest endpoint and validation tests.",
                "resources": [
                    {
                        "title": "Hallucinated Untrusted Blog",
                        "source": "FakeBlog",
                        "url": "https://totally-made-up-blog.example.org/fastapi",
                    }
                ],
            }
        ],
    }

    sanitized = _sanitize_resources_for_phases(raw_llm_output)
    validated = GeneratedRoadmapPlan.model_validate(sanitized)
    assert len(validated.phases[0].resources) >= 1
    for res in validated.phases[0].resources:
        assert is_trusted_resource_url(res.url)
        assert "totally-made-up-blog" not in res.url
