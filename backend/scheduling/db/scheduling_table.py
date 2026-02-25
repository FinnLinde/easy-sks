"""SQLAlchemy ORM model for the ``card_scheduling_info`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CardSchedulingInfoRow(Base):
    """Persistent representation of FSRS scheduling state for a card."""

    __tablename__ = "card_scheduling_info"
    __table_args__ = (
        Index("ix_card_scheduling_info_user_id_due", "user_id", "due"),
    )

    user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    card_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state: Mapped[int] = mapped_column(SmallInteger, default=0)
    stability: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    elapsed_days: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_days: Mapped[int] = mapped_column(Integer, default=0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)
    due: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_review: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
