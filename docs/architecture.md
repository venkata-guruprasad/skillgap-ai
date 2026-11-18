# SkillGap AI – System Architecture (Phase 1)

## High-Level Overview

SkillGap AI follows a modular, three-tier full-stack architecture:

1. **Presentation Layer (`frontend/`)**:
   - React 19 + Vite + Tailwind CSS v4 (`@tailwindcss/vite`)
   - React Router for modular multi-page navigation
   - Centralized Axios client (`src/services/api.js`) configured via `VITE_API_BASE_URL`
   - Recharts for interactive skill gap & career analytics visualizations

2. **Application & API Layer (`backend/`)**:
   - FastAPI with modular separation of `routes/`, `services/`, `schemas/`, `models/`, `ml/`, and `utils/`
   - Pydantic v2 + `pydantic-settings` for strongly typed environment configuration
   - CORS middleware permitting communication with the React frontend
   - Health-check endpoints (`GET /api/health` and `GET /api/health/db`)

3. **Data Layer (`database/` & `backend/alembic/`)**:
   - PostgreSQL 16 relational database
   - SQLAlchemy 2.0 ORM models mapped to core domain entities (`users`, `skills`, `career_roles`, `career_role_skills`, `resumes`, `resume_skills`, `job_descriptions`, `skill_gap_analyses`, `learning_roadmaps`)
   - Alembic migration framework with environment-driven connection URLs (no hardcoded credentials)
   - Initial SQL DDL (`database/schema.sql`) and seed dataset (`database/seed_data.sql`)

## Planned AI/ML Pipeline (Phases 2–4)

The `backend/app/ml/`, `data/`, and `models/` directories are provisioned for:
- **Resume Parsing**: PyMuPDF (PDF) and python-docx (DOCX)
- **Skill Extraction**: spaCy + NLTK pipelines normalized against the `skills` taxonomy
- **Semantic Matching & Career Prediction**: Sentence Transformers embeddings + Scikit-learn classifiers
- **Roadmap Generation**: Priority-ranked milestone builder stored in `learning_roadmaps`
