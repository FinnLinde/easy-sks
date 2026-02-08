"""SQLAlchemy ORM model for the ``review_logs`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ReviewLogRow(Base):
    """Persistent representation of a single review event."""

    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    review_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
