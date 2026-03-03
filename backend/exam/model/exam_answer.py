from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class ExamAnswer:
    """Student answer state and evaluation payload for one question."""

    session_id: str
    card_id: str
    question_number: int
    id: str = field(default_factory=lambda: str(uuid4()))
    student_answer: str = ""
    answered_at: datetime | None = None
    score: float | None = None
    is_correct: bool | None = None
    feedback: str | None = None
    errors: list[str] = field(default_factory=list)
