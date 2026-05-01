"""SQLAlchemy ORM models for exam session persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ExamSessionRow(Base):
    """Persistent representation of an exam session lifecycle."""

    __tablename__ = "exam_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sheet_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    total_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    time_over: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ExamAnswerRow(Base):
    """Persistent answer + evaluation payload for one exam question."""

    __tablename__ = "exam_answers"
    __table_args__ = (
        UniqueConstraint("session_id", "card_id", name="uq_exam_answers_session_card"),
        Index("ix_exam_answers_session_id", "session_id"),
        Index("ix_exam_answers_session_question", "session_id", "question_number"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    card_id: Mapped[str] = mapped_column(String(36), ForeignKey("cards.card_id"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    student_answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    errors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
