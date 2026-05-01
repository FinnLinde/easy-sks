"""OpenAI-backed evaluator for free-text exam answers."""

from __future__ import annotations

import json
import re

from openai import AsyncOpenAI

from exam.model.exam_result import ExamEvaluation
from exam.service.exam_evaluator_port import (
    ExamEvaluatorCapabilities,
    ExamEvaluationRequest,
)
from exam.service.heuristic_exam_evaluator import HeuristicExamEvaluator


class OpenAiExamEvaluator:
    """Evaluates answers with OpenAI and falls back to deterministic scoring."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._fallback = HeuristicExamEvaluator()

    async def evaluate(self, request: ExamEvaluationRequest) -> ExamEvaluation:
        if not request.student_answer.strip():
            return self._fallback.evaluate_sync(request)

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Du bewertest SKS-Pruefungsantworten streng und fair. "
                            "Antworte ausschliesslich als JSON-Objekt."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _build_user_prompt(request),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=self._timeout_seconds,
            )
            raw = completion.choices[0].message.content or "{}"
            payload = _coerce_json(raw)
            score = _clamp_score(payload.get("score"), request.max_score)
            feedback = str(payload.get("feedback") or "Bewertung abgeschlossen.")
            errors = _normalize_errors(payload.get("errors"))
            is_correct = bool(payload.get("is_correct"))
            if "is_correct" not in payload:
                is_correct = score >= (request.max_score * 0.75)

            return ExamEvaluation(
                score=score,
                is_correct=is_correct,
                feedback=feedback,
                errors=errors,
            )
        except Exception:
            fallback = self._fallback.evaluate_sync(request)
            return ExamEvaluation(
                score=fallback.score,
                is_correct=fallback.is_correct,
                feedback=(
                    "Automatische KI-Bewertung war nicht verfuegbar. "
                    f"{fallback.feedback}"
                ),
                errors=fallback.errors,
            )

    def capabilities(self) -> ExamEvaluatorCapabilities:
        return ExamEvaluatorCapabilities(
            provider="openai",
            model=self._model,
            deterministic=False,
            notes="Falls OpenAI nicht verfuegbar ist, wird heuristisch bewertet.",
        )


def _build_user_prompt(request: ExamEvaluationRequest) -> str:
    short_answer_json = json.dumps(request.short_answer, ensure_ascii=False)
    return (
        "Bewerte die Antwort zu einer SKS-Pruefungsfrage.\n"
        f"Frage: {request.question_text}\n"
        f"Referenzstichpunkte: {short_answer_json}\n"
        f"Vollstaendige Referenz: {request.reference_answer}\n"
        f"Antwort des Prueflings: {request.student_answer}\n\n"
        f"Bewerte mit ganzen Punkten von 0 bis {int(request.max_score)}. "
        "Gib nur JSON zurueck: "
        "{\"score\": number, \"is_correct\": boolean, \"errors\": string[], \"feedback\": string}"
    )


def _coerce_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Be defensive in case the model wraps JSON in Markdown fences.
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def _clamp_score(value: object, max_score: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = 0.0

    bounded = max(0.0, min(max_score, parsed))
    return float(round(bounded))


def _normalize_errors(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []
