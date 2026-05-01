"""OpenAI-backed evaluator for navigation task answers."""

from __future__ import annotations

import json
import re

from openai import AsyncOpenAI

from navigation.service.heuristic_navigation_evaluator import HeuristicNavigationEvaluator
from navigation.service.navigation_evaluator_port import (
    NavigationEvaluation,
    NavigationEvaluationRequest,
)


class OpenAiNavigationEvaluator:
    """Evaluates navigation answers with OpenAI, falls back to heuristic scoring."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._fallback = HeuristicNavigationEvaluator()

    async def evaluate(self, request: NavigationEvaluationRequest) -> NavigationEvaluation:
        if not request.student_answer.strip():
            return NavigationEvaluation(
                score=0.0, is_correct=False, feedback="Keine Antwort eingegeben."
            )

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_user_prompt(request)},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=self._timeout_seconds,
            )
            raw = completion.choices[0].message.content or "{}"
            payload = _coerce_json(raw)
            score = _clamp_score(payload.get("score"), request.max_score)
            feedback = str(payload.get("feedback") or "Bewertung abgeschlossen.")
            is_correct = bool(payload.get("is_correct"))
            if "is_correct" not in payload:
                is_correct = score >= (request.max_score * 0.75)

            return NavigationEvaluation(
                score=score, is_correct=is_correct, feedback=feedback
            )
        except Exception:
            fallback = await self._fallback.evaluate(request)
            return NavigationEvaluation(
                score=fallback.score,
                is_correct=fallback.is_correct,
                feedback=(
                    "Automatische KI-Bewertung war nicht verfügbar. "
                    f"{fallback.feedback}"
                ),
            )


_SYSTEM_PROMPT = (
    "Du bewertest Antworten zu SKS-Navigationsaufgaben (Kartenaufgaben). "
    "Diese Aufgaben erfordern Berechnungen auf der Seekarte, Gezeitenrechnung, "
    "Kursberechnungen, Peilungen und Beschreibungen von Seezeichen. "
    "Bewerte streng aber fair. Bei numerischen Werten beachte die angegebenen "
    "Toleranzen. Bei beschreibenden Antworten prüfe, ob alle wesentlichen "
    "Merkmale genannt wurden. "
    "Antworte ausschließlich als JSON-Objekt."
)


def _build_user_prompt(request: NavigationEvaluationRequest) -> str:
    sub_q_text = "\n".join(f"  - {q}" for q in request.sub_questions) if request.sub_questions else "(keine)"
    key_answers_text = (
        "\n".join(f"  - {a}" for a in request.key_answers) if request.key_answers else "(keine numerischen Schlüsselwerte)"
    )

    return (
        "Bewerte die Antwort zu einer SKS-Navigationsaufgabe.\n\n"
        f"Aufgabenkontext:\n{request.context}\n\n"
        f"Teilfragen:\n{sub_q_text}\n\n"
        f"Schlüsselwerte (mit Toleranzen):\n{key_answers_text}\n\n"
        f"Vollständige Musterlösung:\n{request.solution_text}\n\n"
        f"Antwort des Prüflings:\n{request.student_answer}\n\n"
        f"Bewerte mit Schritten von 0.5 von 0 bis {request.max_score}. "
        "Gib nur JSON zurück: "
        '{"score": number, "is_correct": boolean, "feedback": string}'
    )


def _coerce_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
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
    return round(bounded * 2) / 2  # round to nearest 0.5
