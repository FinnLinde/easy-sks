"""SQLAlchemy ORM model for the ``cards`` table."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CardRow(Base):
    """Persistent representation of a flashcard."""

    __tablename__ = "cards"

    card_id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Front content
    front_text: Mapped[str] = mapped_column(Text, default="")
    front_images: Mapped[list] = mapped_column(JSON, default=list)

    # Answer content
    answer_text: Mapped[str] = mapped_column(Text, default="")
    answer_images: Mapped[list] = mapped_column(JSON, default=list)

    # Short answer as bullet-point list
    short_answer: Mapped[list] = mapped_column(JSON, default=list)

    # Tags (e.g. ["navigation"])
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
