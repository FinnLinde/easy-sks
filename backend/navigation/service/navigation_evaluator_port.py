from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class NavigationEvaluationRequest:
    """Inputs needed to evaluate one navigation task answer."""

    context: str
    sub_questions: list[str]
    key_answers: list[str]
    solution_text: str
    student_answer: str
    max_score: float


@dataclass(frozen=True)
class NavigationEvaluation:
    """Structured evaluation output for a single navigation answer."""

    score: float
    is_correct: bool
    feedback: str


class NavigationEvaluatorPort(Protocol):
    """Port for evaluating navigation task answers."""

    async def evaluate(self, request: NavigationEvaluationRequest) -> NavigationEvaluation: ...
