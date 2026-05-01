from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class StudyAnswerEvaluationRequest:
    """Input contract for study answer evaluation backends."""

    question_text: str
    short_answer: list[str]
    reference_answer: str
    user_answer: str
    max_points: float


@dataclass(frozen=True)
class StudyAnswerEvaluationPayload:
    """Evaluator output independent from API/controller concerns."""

    awarded_points: float
    max_points: float
    reasoning_summary: str
    mistakes: list[str] = field(default_factory=list)
    missing_points: list[str] = field(default_factory=list)
    improved_answer_suggestion: str = ""


class StudyAnswerEvaluatorPort(Protocol):
    """Port for AI/non-AI study answer validation implementations."""

    async def evaluate(
        self,
        request: StudyAnswerEvaluationRequest,
    ) -> StudyAnswerEvaluationPayload:
        ...
