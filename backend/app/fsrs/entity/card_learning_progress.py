from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.fsrs.model.defaults import (
    DEFAULT_INITIAL_DIFFICULTY,
    DEFAULT_INITIAL_STABILITY,
)
from app.fsrs.model.enums import CardState

from .base import Base


class CardLearningProgress(Base):
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

    stability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=DEFAULT_INITIAL_STABILITY,
    )
    difficulty: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=DEFAULT_INITIAL_DIFFICULTY,
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
        default=CardState.NEW,
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
