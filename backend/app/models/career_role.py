"""CareerRole and CareerRoleSkill ORM models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CareerRole(Base):
    __tablename__ = "career_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avg_salary_usd: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    demand_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CareerRoleSkill(Base):
    __tablename__ = "career_role_skills"
    __table_args__ = (
        UniqueConstraint("career_role_id", "skill_id", name="uq_career_role_skill"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    career_role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    importance_weight: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), nullable=False, default=Decimal("1.00")
    )
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
