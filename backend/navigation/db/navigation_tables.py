"""SQLAlchemy ORM models for navigation exam persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class NavigationTaskRow(Base):
    """Persistent representation of a navigation exam task."""

    __tablename__ = "navigation_tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sheet_number: Mapped[int] = mapped_column(Integer, nullable=False)
    task_number: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    context: Mapped[str] = mapped_column(Text, default="")
    sub_questions: Mapped[list] = mapped_column(JSON, default=list)
    solution_text: Mapped[str] = mapped_column(Text, default="")
    key_answers: Mapped[list] = mapped_column(JSON, default=list)

    __table_args__ = (
        UniqueConstraint("sheet_number", "task_number", name="uq_nav_tasks_sheet_task"),
        Index("ix_navigation_tasks_sheet_number", "sheet_number"),
    )


class NavigationSessionRow(Base):
    """Persistent representation of a navigation exam session."""

    __tablename__ = "navigation_sessions"

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


class NavigationAnswerRow(Base):
    """Persistent answer + evaluation payload for one navigation task."""

    __tablename__ = "navigation_answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("navigation_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("navigation_tasks.task_id"),
        nullable=False,
    )
    task_number: Mapped[int] = mapped_column(Integer, nullable=False)
    student_answer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("session_id", "task_id", name="uq_nav_answers_session_task"),
        Index("ix_navigation_answers_session_id", "session_id"),
    )
