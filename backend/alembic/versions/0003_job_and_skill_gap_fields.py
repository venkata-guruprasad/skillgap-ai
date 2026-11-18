"""Extend job_descriptions and skill_gap_analyses for Phase 5 JD & Skill Gap Engine.

Revision ID: 0003_job_and_skill_gap_fields
Revises: 0002_resume_analysis_fields
Create Date: 2026-11-18 10:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_job_and_skill_gap_fields"
down_revision: Union[str, None] = "0002_resume_analysis_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_descriptions",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=False,
            server_default="Software Engineering",
        ),
    )
    op.add_column("job_descriptions", sa.Column("location", sa.String(length=150), nullable=True))
    op.add_column("job_descriptions", sa.Column("work_mode", sa.String(length=50), nullable=True))
    op.add_column("job_descriptions", sa.Column("experience_level", sa.String(length=50), nullable=True))
    op.add_column("job_descriptions", sa.Column("salary_range", sa.String(length=100), nullable=True))
    op.add_column(
        "job_descriptions",
        sa.Column("is_sample", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_job_descriptions_category", "job_descriptions", ["category"])
    op.create_index("ix_job_descriptions_is_sample", "job_descriptions", ["is_sample"])
    op.create_index("ix_job_descriptions_user_id", "job_descriptions", ["user_id"])

    op.add_column(
        "skill_gap_analyses",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.alter_column("skill_gap_analyses", "resume_id", existing_type=sa.Integer(), nullable=True)
    op.create_index("ix_skill_gap_analyses_user_id", "skill_gap_analyses", ["user_id"])
    op.create_index("ix_skill_gap_analyses_jd_id", "skill_gap_analyses", ["job_description_id"])


def downgrade() -> None:
    op.drop_index("ix_skill_gap_analyses_jd_id", table_name="skill_gap_analyses")
    op.drop_index("ix_skill_gap_analyses_user_id", table_name="skill_gap_analyses")
    op.alter_column("skill_gap_analyses", "resume_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("skill_gap_analyses", "user_id")

    op.drop_index("ix_job_descriptions_user_id", table_name="job_descriptions")
    op.drop_index("ix_job_descriptions_is_sample", table_name="job_descriptions")
    op.drop_index("ix_job_descriptions_category", table_name="job_descriptions")
    op.drop_column("job_descriptions", "is_sample")
    op.drop_column("job_descriptions", "salary_range")
    op.drop_column("job_descriptions", "experience_level")
    op.drop_column("job_descriptions", "work_mode")
    op.drop_column("job_descriptions", "location")
    op.drop_column("job_descriptions", "category")
