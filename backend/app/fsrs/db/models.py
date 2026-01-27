from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    SmallInteger,
    UniqueConstraint,
    Uuid,
    desc,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.fsrs.domain.enums import CardState

from .base import Base


class CardLearningProgressModel(Base):
    __tablename__ = "card_learning_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "card_id",
            name="uq_card_learning_progress_user_card",
        ),
        Index("ix_card_learning_progress_user_due", "user_id", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cards.id"),
        nullable=False,
    )

    stability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    state: Mapped[CardState] = mapped_column(
        Enum(CardState, name="card_learning_state"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class CardReviewEventModel(Base):
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
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
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
