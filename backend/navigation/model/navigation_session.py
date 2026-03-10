from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import uuid4

from navigation.model.navigation_answer import NavigationAnswer
from navigation.model.navigation_task import NavigationTask


class NavigationSessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"


@dataclass
class NavigationSession:
    """A user's attempt at one navigation exam sheet (90 min, 30 pts)."""

    user_id: str
    sheet_number: int
    time_limit_minutes: int
    id: str = field(default_factory=lambda: str(uuid4()))
    status: NavigationSessionStatus = NavigationSessionStatus.IN_PROGRESS
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
class NavigationSessionQuestion:
    """Read model: a task within a session paired with the user's answer."""

    task_number: int
    task: NavigationTask
    answer: NavigationAnswer


@dataclass(frozen=True)
class NavigationSessionDetails:
    """Read model combining a session with all its task/answer pairs."""

    session: NavigationSession
    questions: list[NavigationSessionQuestion]


@dataclass(frozen=True)
class NavigationSessionHistoryItem:
    """Compact entry for the session history list."""

    session_id: str
    sheet_number: int
    status: str
    started_at: datetime
    submitted_at: datetime | None
    total_score: float | None
    max_score: float | None
    passed: bool | None
    time_over: bool
