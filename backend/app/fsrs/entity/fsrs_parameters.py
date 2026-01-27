from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.fsrs.model.defaults import DEFAULT_PARAMETERS, DEFAULT_TARGET_RETENTION

from .base import Base


class FsrsParameters(Base):
    __tablename__ = "fsrs_parameters"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_fsrs_parameters_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    weights: Mapped[list[float] | None] = mapped_column(
        JSON,
        nullable=True,
        default=lambda: list(DEFAULT_PARAMETERS),
    )
    target_retention: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=DEFAULT_TARGET_RETENTION,
    )
