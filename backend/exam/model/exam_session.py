from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import uuid4

from card.model.card import Card
from exam.model.exam_answer import ExamAnswer


class ExamSessionStatus(StrEnum):
    """Lifecycle state for an exam session."""

    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"


@dataclass
class ExamSession:
    """Persistent aggregate root for an exam run."""

    sheet_number: int
    time_limit_minutes: int
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ExamSessionStatus = ExamSessionStatus.IN_PROGRESS
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: datetime | None = None
    total_score: float | None = None
    max_score: float | None = None
    passed: bool | None = None
    time_over: bool = False

    @property
    def deadline_at(self) -> datetime:
        return self.started_at + timedelta(minutes=self.time_limit_minutes)

    def is_time_over(self, now: datetime | None = None) -> bool:
        ref = now or datetime.now(timezone.utc)
        return ref >= self.deadline_at


@dataclass(frozen=True)
class ExamSessionQuestion:
    """Question payload used by exam session detail responses."""

    question_number: int
    card: Card
    answer: ExamAnswer


@dataclass(frozen=True)
class ExamSessionDetails:
    """Read model combining a session with all its question rows."""

    session: ExamSession
    questions: list[ExamSessionQuestion]


@dataclass(frozen=True)
class ExamSessionHistoryItem:
    """Compact entry for the exam history list."""

    session_id: str
    sheet_number: int
    status: str
    started_at: datetime
    submitted_at: datetime | None
    total_score: float | None
    max_score: float | None
    passed: bool | None
    time_over: bool
