from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from exam.model.exam_result import ExamEvaluation


@dataclass(frozen=True)
class ExamEvaluationRequest:
    """Inputs needed to evaluate one answer against a reference."""

    question_text: str
    short_answer: list[str]
    reference_answer: str
    student_answer: str
    max_score: float


@dataclass(frozen=True)
class ExamEvaluatorCapabilities:
    """Metadata about the currently active evaluator backend."""

    provider: str
    model: str | None = None
    deterministic: bool = False
    notes: str | None = None


class ExamEvaluatorPort(Protocol):
    """Port for evaluating exam answers."""

    async def evaluate(self, request: ExamEvaluationRequest) -> ExamEvaluation:
        ...

    def capabilities(self) -> ExamEvaluatorCapabilities:
        ...
