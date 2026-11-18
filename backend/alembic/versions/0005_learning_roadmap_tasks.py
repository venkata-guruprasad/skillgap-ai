"""Extend learning_roadmaps and create roadmap_tasks table for Phase 7.

Revision ID: 0005_learning_roadmap_tasks
Revises: 0004_career_predictions
Create Date: 2026-11-18 10:20:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_learning_roadmap_tasks"
down_revision: Union[str, None] = "0004_career_predictions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "learning_roadmaps",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.alter_column(
        "learning_roadmaps",
        "analysis_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column(
            "target_role",
            sa.String(length=150),
            nullable=False,
            server_default="Full Stack Developer",
        ),
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column("duration_days", sa.Integer(), nullable=False, server_default="30"),
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column(
            "generation_mode",
            sa.String(length=50),
            nullable=False,
            server_default="deterministic",
        ),
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column("summary_explanation", sa.Text(), nullable=True),
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "learning_roadmaps",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_learning_roadmaps_user_id", "learning_roadmaps", ["user_id"])

    op.create_table(
        "roadmap_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "roadmap_id",
            sa.Integer(),
            sa.ForeignKey("learning_roadmaps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("phase_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("week_label", sa.String(length=40), nullable=False, server_default="Week 1"),
        sa.Column("skill_name", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("task_type", sa.String(length=40), nullable=False, server_default="study"),
        sa.Column("estimated_hours", sa.Integer(), nullable=False, server_default="3"),
        sa.Column(
            "resources",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_roadmap_tasks_id", "roadmap_tasks", ["id"])
    op.create_index("ix_roadmap_tasks_roadmap_id", "roadmap_tasks", ["roadmap_id"])


def downgrade() -> None:
    op.drop_index("ix_roadmap_tasks_roadmap_id", table_name="roadmap_tasks")
    op.drop_index("ix_roadmap_tasks_id", table_name="roadmap_tasks")
    op.drop_table("roadmap_tasks")

    op.drop_index("ix_learning_roadmaps_user_id", table_name="learning_roadmaps")
    op.drop_column("learning_roadmaps", "is_active")
    op.drop_column("learning_roadmaps", "preferences")
    op.drop_column("learning_roadmaps", "summary_explanation")
    op.drop_column("learning_roadmaps", "generation_mode")
    op.drop_column("learning_roadmaps", "duration_days")
    op.drop_column("learning_roadmaps", "target_role")
    op.alter_column(
        "learning_roadmaps",
        "analysis_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("learning_roadmaps", "user_id")
