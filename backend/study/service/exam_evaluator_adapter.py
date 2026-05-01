"""Adapter that reuses the exam evaluator stack for study answer validation."""

from __future__ import annotations

from exam.service.exam_evaluator_port import ExamEvaluationRequest, ExamEvaluatorPort
from study.service.answer_evaluator_port import (
    StudyAnswerEvaluationPayload,
    StudyAnswerEvaluationRequest,
)


class ExamBackedStudyAnswerEvaluator:
    """Bridge between StudyAnswerEvaluatorPort and ExamEvaluatorPort."""

    def __init__(self, exam_evaluator: ExamEvaluatorPort) -> None:
        self._exam_evaluator = exam_evaluator

    async def evaluate(
        self,
        request: StudyAnswerEvaluationRequest,
    ) -> StudyAnswerEvaluationPayload:
        exam_evaluation = await self._exam_evaluator.evaluate(
            ExamEvaluationRequest(
                question_text=request.question_text,
                short_answer=request.short_answer,
                reference_answer=request.reference_answer,
                student_answer=request.user_answer,
                max_score=request.max_points,
            )
        )

        awarded = max(0.0, min(request.max_points, exam_evaluation.score))
        suggestion = _build_improved_suggestion(
            short_answer=request.short_answer,
            reference_answer=request.reference_answer,
            existing_feedback=exam_evaluation.feedback,
        )
        mistakes = list(exam_evaluation.errors)

        return StudyAnswerEvaluationPayload(
            awarded_points=awarded,
            max_points=request.max_points,
            reasoning_summary=exam_evaluation.feedback,
            mistakes=mistakes,
            missing_points=mistakes,
            improved_answer_suggestion=suggestion,
        )


def _build_improved_suggestion(
    short_answer: list[str],
    reference_answer: str,
    existing_feedback: str,
) -> str:
    if short_answer:
        return "Beispielstruktur: " + "; ".join(short_answer[:4])

    condensed_reference = " ".join(reference_answer.split())
    if condensed_reference:
        return condensed_reference[:260]

    return existing_feedback
