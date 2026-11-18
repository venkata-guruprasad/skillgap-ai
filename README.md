# SkillGap AI — AI-Powered Skill Gap & Career Prediction System

SkillGap AI is a full-stack career intelligence platform that analyzes student and job-seeker resumes with NLP, evaluates weighted and semantic skill gaps against real or sample job descriptions, predicts top-matching career tracks using a trained machine learning pipeline, and generates persistent 30-, 60-, and 90-day personalized learning roadmaps with verified educational resources.

---

## Key Features

- **Secure JWT Authentication & User Isolation**: PBKDF2-HMAC-SHA256 salted password hashing (120,000 iterations), HS256 JWT tokens, owner-scoped API enforcement, and live profile editing (`PATCH /api/auth/me`).
- **AI Resume Analyzer & NLP Skill Extraction**: Secure PDF (`PyMuPDF`) and DOCX (`python-docx`) uploads up to 5 MB with SHA-256 duplicate detection, scanned-PDF detection, PII redaction, section segmentation, ATS scoring, and context-aware `spaCy` + `NLTK` technical & soft skill extraction with evidence snippets.
- **Job Description Analyzer & Semantic Skill Gap Engine**: 8 clearly labeled seeded sample job descriptions plus custom JD parsing (`POST /api/jobs`), combining exact/synonym matching with `sentence-transformers/all-MiniLM-L6-v2` semantic similarity, required skill importance weights, and separate preferred skill scoring.
- **12-Role ML Career Prediction Engine**: Trained Scikit-learn `CalibratedLinearSVC` classifier (`91.67%` held-out accuracy / `91.60%` macro F1 on our clearly labeled leak-free synthetic benchmark dataset) combined with MiniLM profile embeddings and weighted Skill Gap scores to rank the top 5 roles with explainable score breakdowns.
- **Personalized 30/60/90-Day AI Learning Roadmaps**: Structured multi-phase plans (learning objectives, weekly tasks, practical exercises, portfolio mini projects, assessment checkpoints, and strictly validated trusted resource URLs from Official Documentation, freeCodeCamp, Coursera, edX, Kaggle, and YouTube). Supports optional OpenAI/Gemini LLM integration via environment variables with Pydantic validation and a full deterministic engine when no API key is configured.
- **Persistent Progress Tracking & Live Dashboard Analytics**: Real-time database persistence for completed tasks, milestone progression, learning history resumption, and aggregated dashboard KPIs & activity feeds (`GET /api/dashboard/analytics`).

---

## Technology Stack

| Layer | Technologies |
| --- | --- |
| **Frontend** | React 19, Vite 6, Tailwind CSS v4, React Router v7, Recharts, Lucide Icons, Axios |
| **Backend** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2, Alembic, PyJWT |
| **NLP & ML** | spaCy (`en_core_web_sm`), NLTK, PyMuPDF (`fitz`), `python-docx`, Sentence Transformers (`all-MiniLM-L6-v2`), Scikit-learn, Joblib |
| **Database** | PostgreSQL 16 (production / Docker) with automatic SQLite local dev fallback when `POSTGRES_*` env vars are unset |
| **Deployment** | Docker, Docker Compose, Nginx reverse proxy with SPA fallback & 6 MB upload proxy support |

---

## Architecture

```text
skillgap-ai/
├── frontend/                   # React + Vite + Tailwind CSS v4 SaaS UI (11 pages)
│   ├── src/
│   │   ├── components/         # Layout, Sidebar, Header, MetricCard, DemoBadge, Toast
│   │   ├── context/            # AppContext (JWT auth, live API sync, global workspace state)
│   │   ├── pages/              # Landing, Login, Register, Dashboard, Resume, SkillGap, Career, Jobs, Roadmap, Progress, Settings
│   │   ├── services/           # Axios API client (api.js)
│   │   └── tests/              # Automated Node test suite (frontend.test.mjs)
│   ├── Dockerfile              # Multi-stage Node build + Nginx runtime
│   └── nginx.conf              # /api proxy, 6 MB upload body limit, security headers, SPA routing
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── ml/                 # NLP resume pipeline, semantic matcher, skill gap engine, career ML, roadmap AI/LLM engine
│   │   ├── models/             # SQLAlchemy ORM models (User, Resume, JobDescription, SkillGapAnalysis, CareerPredictionRecord, LearningRoadmap, RoadmapTask)
│   │   ├── routes/             # Modular FastAPI routers (/api/*)
│   │   ├── schemas/            # Pydantic v2 request/response contracts
│   │   ├── services/           # Business logic & DB queries
│   │   ├── utils/              # Security (PBKDF2 + JWT) & structured logging
│   │   └── tests/              # Pytest unit, integration, security & 10-step user journey tests
│   ├── alembic/                # Database migrations (0001 -> 0005)
│   └── Dockerfile              # Python 3.12 + spaCy/NLTK model setup + Uvicorn
├── database/                   # PostgreSQL schema.sql & seed_data.sql
├── models/trained/             # Saved career ML model bundle & evaluation report
├── docker-compose.yml          # PostgreSQL 16 + FastAPI Backend + Nginx Frontend
└── .env.example                # Environment variable template (no real secrets)
```

---

## Installation

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** and **npm**
- **PostgreSQL 16** (optional for local development — SQLite fallback works out of the box when `APP_ENV=development` and PostgreSQL vars are unset)
- **Docker & Docker Compose** (optional, for containerized deployment)

### 1. Clone and configure environment variables
```bash
cp skillgap-ai/.env.example skillgap-ai/.env
```
Edit `skillgap-ai/.env` and set strong values for `SECRET_KEY` and `POSTGRES_PASSWORD`.

### 2. Backend installation
```bash
cd skillgap-ai/backend
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt')"
```

### 3. Frontend installation
```bash
cd skillgap-ai/frontend
npm install
```

---

## Environment Variables

See [`.env.example`](.env.example) for the complete reference:

| Variable | Description | Default |
| --- | --- | --- |
| `APP_ENV` | `development` or `production` | `development` |
| `SECRET_KEY` | JWT signing secret (**required** in non-development environments) | dev-only fallback |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime in minutes | `120` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173,...` |
| `POSTGRES_HOST` / `PORT` / `USER` / `PASSWORD` / `DB` | PostgreSQL connection parameters | empty (uses SQLite in dev) |
| `DATABASE_URL` | Optional full SQLAlchemy connection URL | unset |
| `LLM_PROVIDER` | Optional roadmap LLM provider (`none`, `openai`, `gemini`) | `none` |
| `LLM_API_KEY` | Optional API key for configured LLM provider (never exposed) | empty |
| `LLM_MODEL` | Optional LLM model override (`gpt-4o-mini`, `gemini-2.0-flash`) | provider default |
| `VITE_API_BASE_URL` | Backend base URL for frontend Axios client | `http://localhost:8000` |

---

## Database Setup

### PostgreSQL (Production / Local PostgreSQL)
1. Set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` (or `DATABASE_URL`) in `.env`.
2. Apply Alembic migrations from `skillgap-ai/backend`:
   ```bash
   alembic upgrade head
   ```
   Or initialize directly via `database/schema.sql` and `database/seed_data.sql` (automatically executed by the Docker PostgreSQL container on first boot).

### Local SQLite Development Fallback
When `APP_ENV=development` and PostgreSQL environment variables are empty, FastAPI automatically initializes `skillgap-ai/backend/skillgap_dev.db`, seeds the 8 labeled sample job descriptions, and creates a development demo account (`alex.rivera@university.edu` / `demo-password-2026`).

---

## Backend Startup

```bash
cd skillgap-ai/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Interactive Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

---

## Frontend Startup

```bash
cd skillgap-ai/frontend
npm run dev
```

- Local Web App: `http://localhost:5173`
- Production build: `npm run build`

---

## Docker Deployment

Ensure `.env` exists in `skillgap-ai/` with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `SECRET_KEY` (>= 32 random chars), and `APP_ENV=production` set, then run:

```bash
cd skillgap-ai
docker compose up --build -d
```

Services started:
- **PostgreSQL 16 (`db`)**: Persistent volume `postgres_data`.
- **FastAPI Backend (`backend`)**: Port `8000`, non-root `appuser`, baked-in `en_core_web_sm`, `punkt_tab`, `all-MiniLM-L6-v2`, and `career_model_bundle.joblib` (zero runtime model downloads), automatic `alembic upgrade head` via `entrypoint.sh`, and persistent volumes `uploads_data` (`/data/uploads`) and `hf_cache`.
- **React + Nginx Frontend (`frontend`)**: Port `5173` (mapped to container port `80`), proxying `/api/*` with `client_max_body_size 6m` and security headers.

Check container health:
```bash
docker compose ps
docker compose logs -f backend
```

Stop services (preserving database volume):
```bash
docker compose down
```

---

## Cloud Production Deployment (Vercel + Render/Railway + Neon/Supabase)

See the complete **[Production Deployment Guide (DEPLOYMENT.md)](DEPLOYMENT.md)** for exact instructions, environment variable tables, AI/ML RAM sizing, and troubleshooting across:
- **Frontend**: Vercel (`frontend/vercel.json`)
- **Backend**: Render (`render.yaml`, Standard 2 GB plan) or Railway / Fly.io
- **Database**: Neon or Supabase Managed PostgreSQL 16 (`?sslmode=require`)

---

## API Documentation

Interactive OpenAPI docs are served at `GET /docs` and `GET /redoc`.

| Group | Method & Path | Auth | Purpose |
| --- | --- | --- | --- |
| **Health** | `GET /api/health`, `GET /api/health/db` | Public | Application & database health checks |
| **Auth** | `POST /api/auth/register`, `POST /api/auth/login` | Public | Register account & obtain JWT Bearer token |
| **Auth** | `GET /api/auth/me`, `PATCH /api/auth/me` | Bearer | Retrieve or update authenticated user profile |
| **Dashboard** | `GET /api/dashboard/analytics` | Bearer | Aggregated counts, latest resume, ML career matches, roadmap progress & DB activity feed |
| **Resume** | `POST /api/resume/upload` | Bearer | Upload PDF/DOCX (<= 5 MB), extract text & NLP skills |
| **Resume** | `GET /api/resume/history`, `GET /api/resume/{id}`, `DELETE /api/resume/{id}` | Bearer | Manage user-owned resume analyses |
| **Skills** | `POST /api/skills/extract` | Bearer | Context-aware NLP skill extraction from raw text |
| **Jobs** | `GET /api/jobs`, `GET /api/jobs/{id}`, `POST /api/jobs` | Public / Bearer (`POST`) | Browse seeded sample jobs & parse/save custom job descriptions |
| **Skill Gap** | `POST /api/analysis/skill-gap`, `GET /api/analysis/history`, `GET /api/analysis/{id}` | Bearer | Weighted + MiniLM semantic skill gap analysis & history |
| **Career ML** | `POST /api/career/predict`, `GET /api/career/recommendations` | Bearer | 12-role ML career prediction (top 5 ranked roles + evaluation metrics) |
| **Roadmap** | `POST /api/roadmap/generate`, `GET /api/roadmap`, `GET /api/roadmap/{id}` | Bearer | Generate & retrieve 30/60/90-day personalized roadmaps & history |
| **Roadmap** | `PATCH /api/roadmap/tasks/{id}` | Bearer | Toggle persistent task completion & recalculate milestone progress |

---

## Testing Instructions

### Backend Tests (`pytest`)
Includes health, resume NLP/validation, semantic skill gap, 12-role ML career prediction, 30/60/90-day roadmap persistence, security audit (headers, SQLi safety, cross-user isolation), ML singleton caching, and the complete 10-step end-to-end user journey:

```bash
cd skillgap-ai/backend
pytest -v
```

### Frontend Tests & Production Build
```bash
cd skillgap-ai/frontend
npm test
npm run build
```

### Retrain & Evaluate Career ML Model (Optional)
```bash
cd skillgap-ai/backend
python -m app.ml.career.model_trainer
```
