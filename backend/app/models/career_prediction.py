"""CareerPrediction ORM model for persisting user career recommendation runs."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

PortableJSON = JSON().with_variant(JSONB, "postgresql")


class CareerPredictionRecord(Base):
    __tablename__ = "career_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    input_profile: Mapped[Dict[str, Any]] = mapped_column(
        PortableJSON, nullable=False, default=dict
    )
    recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(
        PortableJSON, nullable=False, default=list
    )
    model_metadata: Mapped[Dict[str, Any]] = mapped_column(
        PortableJSON, nullable=False, default=dict
    )
    selected_classifier: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
