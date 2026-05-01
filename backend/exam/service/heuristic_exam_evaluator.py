"""Deterministic fallback evaluator used when no AI provider is configured."""

from __future__ import annotations

import re
from collections.abc import Iterable

from exam.model.exam_result import ExamEvaluation
from exam.service.exam_evaluator_port import (
    ExamEvaluatorCapabilities,
    ExamEvaluationRequest,
)


class HeuristicExamEvaluator:
    """Simple rubric-style keyword matching evaluator.

    This fallback keeps the feature operational in local environments without
    external model credentials.
    """

    def evaluate_sync(self, request: ExamEvaluationRequest) -> ExamEvaluation:
        student_text = request.student_answer.strip()
        if not student_text:
            return ExamEvaluation(
                score=0.0,
                is_correct=False,
                feedback="Keine Antwort abgegeben.",
                errors=["Es wurde keine Antwort eingereicht."],
            )

        phrases = _extract_phrases(request.short_answer, request.reference_answer)
        if not phrases:
            return ExamEvaluation(
                score=request.max_score,
                is_correct=True,
                feedback="Antwort eingereicht. Es lagen keine Referenzkriterien vor.",
                errors=[],
            )

        student_tokens = set(_tokenize(student_text))
        covered: list[str] = []
        missing: list[str] = []

        for phrase in phrases:
            if _phrase_is_covered(phrase, student_tokens):
                covered.append(phrase)
            else:
                missing.append(phrase)

        ratio = len(covered) / len(phrases)
        raw_score = ratio * request.max_score
        score = float(round(raw_score))
        is_correct = score >= (request.max_score * 0.75)

        if ratio >= 0.9:
            feedback = "Sehr gute Antwort, die wichtigsten Kernpunkte sind enthalten."
        elif ratio >= 0.55:
            feedback = "Teilweise korrekt, einige Kernpunkte fehlen noch."
        else:
            feedback = "Zu viele Kernpunkte fehlen fuer eine ausreichende Bewertung."

        return ExamEvaluation(
            score=max(0.0, min(request.max_score, score)),
            is_correct=is_correct,
            feedback=feedback,
            errors=[f"Fehlender Kernpunkt: {point}" for point in missing[:5]],
        )

    async def evaluate(self, request: ExamEvaluationRequest) -> ExamEvaluation:
        return self.evaluate_sync(request)

    def capabilities(self) -> ExamEvaluatorCapabilities:
        return ExamEvaluatorCapabilities(
            provider="heuristic",
            model=None,
            deterministic=True,
            notes="Keyword-based fallback evaluator",
        )


def _extract_phrases(short_answer: list[str], reference_answer: str) -> list[str]:
    cleaned_short = [part.strip() for part in short_answer if part.strip()]
    if cleaned_short:
        return cleaned_short

    sentence_candidates = [
        sentence.strip()
        for sentence in re.split(r"[\n\.;]+", reference_answer)
        if sentence.strip()
    ]
    return sentence_candidates[:5]


def _tokenize(text: str) -> list[str]:
    return [token for token in re.split(r"[^a-zA-Z0-9äöüÄÖÜß]+", text.lower()) if token]


def _phrase_is_covered(phrase: str, student_tokens: set[str]) -> bool:
    words = [w for w in _tokenize(phrase) if len(w) >= 4]
    if not words:
        return False
    matched = sum(1 for word in words if word in student_tokens)
    return matched >= max(1, len(words) // 2)
