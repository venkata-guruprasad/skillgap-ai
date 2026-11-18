"""Initial SkillGap AI database schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-18 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("name", name="uq_skills_name"),
    )
    op.create_index("ix_skills_id", "skills", ["id"])
    op.create_index("ix_skills_name", "skills", ["name"], unique=True)
    op.create_index("ix_skills_category", "skills", ["category"])

    op.create_table(
        "career_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("avg_salary_usd", sa.Integer(), nullable=True),
        sa.Column("demand_level", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("title", name="uq_career_roles_title"),
    )
    op.create_index("ix_career_roles_id", "career_roles", ["id"])

    op.create_table(
        "career_role_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "career_role_id",
            sa.Integer(),
            sa.ForeignKey("career_roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.Integer(),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("importance_weight", sa.Numeric(4, 2), nullable=False, server_default="1.00"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill"),
    )
    op.create_index("ix_career_role_skills_id", "career_role_skills", ["id"])
    op.create_index("ix_career_role_skills_role", "career_role_skills", ["career_role_id"])

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_resumes_id", "resumes", ["id"])
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    op.create_table(
        "resume_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "resume_id",
            sa.Integer(),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.Integer(),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False, server_default="extracted"),
        sa.UniqueConstraint("resume_id", "skill_id", name="uq_resume_skill"),
    )
    op.create_index("ix_resume_skills_id", "resume_skills", ["id"])

    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("company", sa.String(length=200), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("extracted_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_job_descriptions_id", "job_descriptions", ["id"])

    op.create_table(
        "skill_gap_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "resume_id",
            sa.Integer(),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_role_id",
            sa.Integer(),
            sa.ForeignKey("career_roles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "job_description_id",
            sa.Integer(),
            sa.ForeignKey("job_descriptions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("match_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("matched_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("missing_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("recommendations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_skill_gap_analyses_id", "skill_gap_analyses", ["id"])
    op.create_index("ix_skill_gap_analyses_resume", "skill_gap_analyses", ["resume_id"])

    op.create_table(
        "learning_roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("skill_gap_analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("estimated_weeks", sa.Integer(), nullable=True),
        sa.Column(
            "milestones",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_learning_roadmaps_id", "learning_roadmaps", ["id"])
    op.create_index("ix_learning_roadmaps_analysis", "learning_roadmaps", ["analysis_id"])


def downgrade() -> None:
    op.drop_table("learning_roadmaps")
    op.drop_table("skill_gap_analyses")
    op.drop_table("job_descriptions")
    op.drop_table("resume_skills")
    op.drop_table("resumes")
    op.drop_table("career_role_skills")
    op.drop_table("career_roles")
    op.drop_table("skills")
    op.drop_table("users")
