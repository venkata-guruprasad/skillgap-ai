"""Add career_predictions table for Phase 6 ML Career Prediction Engine.

Revision ID: 0004_career_predictions
Revises: 0003_job_and_skill_gap_fields
Create Date: 2026-11-18 10:15:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_career_predictions"
down_revision: Union[str, None] = "0003_job_and_skill_gap_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "career_predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            sa.Integer(),
            sa.ForeignKey("resumes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "input_profile",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "recommendations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "model_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("selected_classifier", sa.String(length=80), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_career_predictions_id", "career_predictions", ["id"])
    op.create_index("ix_career_predictions_user_id", "career_predictions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_career_predictions_user_id", table_name="career_predictions")
    op.drop_index("ix_career_predictions_id", table_name="career_predictions")
    op.drop_table("career_predictions")
