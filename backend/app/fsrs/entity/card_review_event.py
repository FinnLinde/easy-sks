from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    SmallInteger,
    desc,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CardReviewEvent(Base):
    __tablename__ = "card_review_event"
    __table_args__ = (
        Index(
            "ix_card_review_event_user_reviewed_at",
            "user_id",
            desc("reviewed_at"),
        ),
        Index(
            "ix_card_review_event_user_card_reviewed_at",
            "user_id",
            "card_id",
            desc("reviewed_at"),
        ),
        CheckConstraint(
            "rating >= 0 AND rating <= 3",
            name="ck_card_review_event_rating",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cards.id"),
        nullable=False,
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )
    time_to_answer_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    progress_snapshot: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
