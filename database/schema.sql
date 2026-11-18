-- =============================================================================
-- SkillGap AI – Initial PostgreSQL Schema
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    category VARCHAR(80) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS career_roles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL UNIQUE,
    category VARCHAR(100),
    description TEXT,
    avg_salary_usd INTEGER,
    demand_level VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS career_role_skills (
    id SERIAL PRIMARY KEY,
    career_role_id INTEGER NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance_weight NUMERIC(4, 2) NOT NULL DEFAULT 1.00,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_career_role_skill UNIQUE (career_role_id, skill_id)
);

CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    file_size_bytes INTEGER,
    file_hash VARCHAR(64),
    extraction_status VARCHAR(40) NOT NULL DEFAULT 'completed',
    raw_text TEXT,
    parsed_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resume_skills (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    confidence_score NUMERIC(5, 4),
    source VARCHAR(50) NOT NULL DEFAULT 'extracted',
    CONSTRAINT uq_resume_skill UNIQUE (resume_id, skill_id)
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200),
    category VARCHAR(100) NOT NULL DEFAULT 'Software Engineering',
    location VARCHAR(150),
    work_mode VARCHAR(50),
    experience_level VARCHAR(50),
    salary_range VARCHAR(100),
    is_sample BOOLEAN NOT NULL DEFAULT FALSE,
    raw_text TEXT NOT NULL,
    extracted_skills JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_gap_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    target_role_id INTEGER REFERENCES career_roles(id) ON DELETE SET NULL,
    job_description_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL,
    match_score NUMERIC(5, 2),
    matched_skills JSONB,
    missing_skills JSONB,
    recommendations JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_roadmaps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    analysis_id INTEGER REFERENCES skill_gap_analyses(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    target_role VARCHAR(150) NOT NULL DEFAULT 'Full Stack Developer',
    duration_days INTEGER NOT NULL DEFAULT 30,
    estimated_weeks INTEGER,
    generation_mode VARCHAR(50) NOT NULL DEFAULT 'deterministic',
    summary_explanation TEXT,
    preferences JSONB,
    milestones JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roadmap_tasks (
    id SERIAL PRIMARY KEY,
    roadmap_id INTEGER NOT NULL REFERENCES learning_roadmaps(id) ON DELETE CASCADE,
    phase_number INTEGER NOT NULL DEFAULT 1,
    week_label VARCHAR(40) NOT NULL DEFAULT 'Week 1',
    skill_name VARCHAR(120) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(40) NOT NULL DEFAULT 'study',
    estimated_hours INTEGER NOT NULL DEFAULT 3,
    resources JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS career_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
    input_profile JSONB NOT NULL DEFAULT '{}'::jsonb,
    recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    selected_classifier VARCHAR(80),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_career_predictions_user ON career_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_file_hash ON resumes(file_hash);
CREATE INDEX IF NOT EXISTS idx_resumes_user_hash ON resumes(user_id, file_hash);
CREATE INDEX IF NOT EXISTS idx_career_role_skills_role ON career_role_skills(career_role_id);
CREATE INDEX IF NOT EXISTS idx_skill_gap_analyses_resume ON skill_gap_analyses(resume_id);
CREATE INDEX IF NOT EXISTS idx_learning_roadmaps_analysis ON learning_roadmaps(analysis_id);
