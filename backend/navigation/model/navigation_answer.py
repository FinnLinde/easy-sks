from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class NavigationAnswer:
    """Student answer state and evaluation payload for one navigation task."""

    session_id: str
    task_id: str
    task_number: int
    id: str = field(default_factory=lambda: str(uuid4()))
    student_answer: str = ""
    answered_at: datetime | None = None
    score: float | None = None
    is_correct: bool | None = None
    feedback: str | None = None
