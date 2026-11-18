"""Add resume metadata columns for Phase 4 NLP analysis and duplicate detection.

Revision ID: 0002_resume_analysis_fields
Revises: 0001_initial_schema
Create Date: 2026-11-18 09:30:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_resume_analysis_fields"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("file_size_bytes", sa.Integer(), nullable=True))
    op.add_column("resumes", sa.Column("file_hash", sa.String(length=64), nullable=True))
    op.add_column(
        "resumes",
        sa.Column(
            "extraction_status",
            sa.String(length=40),
            nullable=False,
            server_default="completed",
        ),
    )
    op.create_index("ix_resumes_file_hash", "resumes", ["file_hash"])
    op.create_index("ix_resumes_user_hash", "resumes", ["user_id", "file_hash"])


def downgrade() -> None:
    op.drop_index("ix_resumes_user_hash", table_name="resumes")
    op.drop_index("ix_resumes_file_hash", table_name="resumes")
    op.drop_column("resumes", "extraction_status")
    op.drop_column("resumes", "file_hash")
    op.drop_column("resumes", "file_size_bytes")
