from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class NavigationQuestionResult:
    """Evaluation result for a single navigation task."""

    task_number: int
    task_id: str
    context: str
    sub_questions: list[str]
    key_answers: list[str]
    solution_text: str
    student_answer: str
    score: float
    max_score: float
    is_correct: bool
    feedback: str


@dataclass(frozen=True)
class NavigationSessionResult:
    """Full result of an evaluated navigation session."""

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
    questions: list[NavigationQuestionResult] = field(default_factory=list)
