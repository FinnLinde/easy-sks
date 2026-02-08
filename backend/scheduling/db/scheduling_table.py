"""SQLAlchemy ORM model for the ``card_scheduling_info`` table."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CardSchedulingInfoRow(Base):
    """Persistent representation of FSRS scheduling state for a card."""

    __tablename__ = "card_scheduling_info"

    card_id: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )
    state: Mapped[int] = mapped_column(SmallInteger, default=0)
    stability: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    elapsed_days: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_days: Mapped[int] = mapped_column(Integer, default=0)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)
    due: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_review: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
