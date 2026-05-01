from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class StudyAnswerVerdict(StrEnum):
    """Categorical quality verdict for free-text study answers."""

    FULL = "full"
    PARTIAL = "partial"
    INCORRECT = "incorrect"


@dataclass(frozen=True)
class StudyAnswerEvaluation:
    """Structured AI evaluation payload returned to the study UI."""

    card_id: str
    awarded_points: float
    max_points: float
    verdict: StudyAnswerVerdict
    reasoning_summary: str
    mistakes: list[str] = field(default_factory=list)
    missing_points: list[str] = field(default_factory=list)
    improved_answer_suggestion: str = ""
    suggested_rating: int = 1
