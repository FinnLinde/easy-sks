"""Simple heuristic evaluator for navigation answers.

Checks whether key answers appear (approximately) in the student's response.
Used as a fallback when no AI evaluator is configured.
"""

from __future__ import annotations

import re

from navigation.service.navigation_evaluator_port import (
    NavigationEvaluation,
    NavigationEvaluationRequest,
)


class HeuristicNavigationEvaluator:
    """Keyword/tolerance-based evaluator for navigation answers."""

    async def evaluate(self, request: NavigationEvaluationRequest) -> NavigationEvaluation:
        if not request.student_answer.strip():
            return NavigationEvaluation(
                score=0.0,
                is_correct=False,
                feedback="Keine Antwort eingegeben.",
            )

        if not request.key_answers:
            return NavigationEvaluation(
                score=round(request.max_score * 0.5, 1),
                is_correct=False,
                feedback=(
                    "Automatische Bewertung nicht möglich – "
                    "bitte mit der Musterlösung vergleichen."
                ),
            )

        matched = 0
        student_normalised = _normalise(request.student_answer)
        for key in request.key_answers:
            value = _extract_value(key)
            if value and value in student_normalised:
                matched += 1

        ratio = matched / len(request.key_answers) if request.key_answers else 0.0
        score = round(request.max_score * ratio, 1)
        is_correct = ratio >= 0.8

        if is_correct:
            feedback = "Alle wesentlichen Werte korrekt."
        elif ratio > 0:
            feedback = (
                f"{matched} von {len(request.key_answers)} Schlüsselwerten erkannt. "
                "Bitte mit der Musterlösung vergleichen."
            )
        else:
            feedback = "Keine übereinstimmenden Werte gefunden. Bitte Musterlösung prüfen."

        return NavigationEvaluation(score=score, is_correct=is_correct, feedback=feedback)

    def capabilities(self):
        return {"provider": "heuristic", "deterministic": True}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _extract_value(key_answer: str) -> str | None:
    """Pull the core numeric value from a key answer like 'KaK = 286° [± 1°]'."""
    match = re.search(r"=\s*(.+?)(?:\s*\[|$)", key_answer)
    if match:
        raw = match.group(1).strip()
        # Strip trailing units (°, ', sm, kn, m, min, h, s) and whitespace
        cleaned = re.sub(r"[\s°']+$", "", raw)
        cleaned = re.sub(r"\s+(?:sm|kn|m|min|h|s|Bft)$", "", cleaned)
        return _normalise(cleaned)
    return None
