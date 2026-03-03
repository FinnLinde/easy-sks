from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ExamEvaluation:
    """Structured evaluation output for a single submitted answer."""

    score: float
    is_correct: bool
    feedback: str
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExamQuestionResult:
    """Result view for one question inside a completed exam session."""

    question_number: int
    card_id: str
    question_text: str
    reference_short_answer: list[str]
    student_answer: str
    score: float
    is_correct: bool
    feedback: str
    errors: list[str]


@dataclass(frozen=True)
class ExamSessionResult:
    """Aggregated result payload for a completed exam session."""

    session_id: str
    sheet_number: int
    status: str
    started_at: datetime
    submitted_at: datetime | None
    time_limit_minutes: int
    time_over: bool
    total_score: float
    max_score: float
    passed: bool
    pass_score_threshold: float
    questions: list[ExamQuestionResult]
