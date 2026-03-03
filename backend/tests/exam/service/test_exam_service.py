from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from card.model.card import Card
from card.model.card_content import CardContent
from exam.model.exam_answer import ExamAnswer
from exam.model.exam_result import ExamEvaluation
from exam.model.exam_session import ExamSession, ExamSessionStatus
from exam.service.exam_evaluator_port import (
    ExamEvaluatorCapabilities,
    ExamEvaluationRequest,
)
from exam.service.exam_service import ExamService


class FakeCardRepository:
    def __init__(self, cards: list[Card]) -> None:
        self._cards = {card.card_id: card for card in cards}

    async def list_all(self) -> list[Card]:
        return list(self._cards.values())

    async def get_by_id(self, card_id: str) -> Card | None:
        return self._cards.get(card_id)


class FakeExamRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, ExamSession] = {}
        self._answers: dict[str, dict[str, ExamAnswer]] = {}

    async def create_session(self, session: ExamSession, answers: list[ExamAnswer]) -> None:
        self._sessions[session.id] = session
        self._answers[session.id] = {answer.card_id: answer for answer in answers}

    async def get_session(self, user_id: str, session_id: str) -> ExamSession | None:
        session = self._sessions.get(session_id)
        if session is None or session.user_id != user_id:
            return None
        return session

    async def save_session(self, session: ExamSession) -> None:
        self._sessions[session.id] = session

    async def list_answers(self, session_id: str) -> list[ExamAnswer]:
        values = list(self._answers.get(session_id, {}).values())
        return sorted(values, key=lambda item: item.question_number)

    async def get_answer(self, user_id: str, session_id: str, card_id: str) -> ExamAnswer | None:
        session = self._sessions.get(session_id)
        if session is None or session.user_id != user_id:
            return None
        return self._answers.get(session_id, {}).get(card_id)

    async def save_answer(self, answer: ExamAnswer) -> None:
        self._answers.setdefault(answer.session_id, {})[answer.card_id] = answer

    async def list_completed_sessions_for_user(self, user_id: str) -> list[ExamSession]:
        sessions = [
            session
            for session in self._sessions.values()
            if session.user_id == user_id and session.status != ExamSessionStatus.IN_PROGRESS
        ]
        return sorted(sessions, key=lambda session: session.started_at, reverse=True)


class ConstantEvaluator:
    def __init__(self, score: float) -> None:
        self._score = score

    async def evaluate(self, request: ExamEvaluationRequest) -> ExamEvaluation:
        return ExamEvaluation(
            score=self._score,
            is_correct=self._score >= 1.5,
            feedback="ok",
            errors=[],
        )

    def capabilities(self) -> ExamEvaluatorCapabilities:
        return ExamEvaluatorCapabilities(provider="test", deterministic=True)


def _build_cards_for_sheet(sheet_number: int, count: int = 30) -> list[Card]:
    return [
        Card(
            card_id=f"sheet-{sheet_number}-{index:02d}",
            front=CardContent(text=f"Question {index}"),
            answer=CardContent(text="Reference answer"),
            short_answer=["core point"],
            tags=["navigation"],
            exam_sheets=[sheet_number],
        )
        for index in range(count)
    ]


@pytest.mark.asyncio
class TestExamService:
    async def test_lists_all_templates(self):
        cards = _build_cards_for_sheet(1) + _build_cards_for_sheet(2)
        service = ExamService(
            exam_repo=FakeExamRepository(),
            card_repo=FakeCardRepository(cards),
            evaluator=ConstantEvaluator(score=2.0),
        )

        templates = await service.list_templates()

        assert len(templates) == 15
        assert templates[0].sheet_number == 1
        assert templates[0].question_count == 30
        assert templates[1].sheet_number == 2
        assert templates[1].question_count == 30
        assert templates[2].sheet_number == 3
        assert templates[2].question_count == 0

    async def test_start_session_requires_full_sheet(self):
        service = ExamService(
            exam_repo=FakeExamRepository(),
            card_repo=FakeCardRepository(_build_cards_for_sheet(1, count=5)),
            evaluator=ConstantEvaluator(score=2.0),
        )

        with pytest.raises(ValueError, match="expected 30"):
            await service.start_session(user_id="u1", sheet_number=1)

    async def test_submit_marks_passed_when_score_reaches_threshold(self):
        repo = FakeExamRepository()
        service = ExamService(
            exam_repo=repo,
            card_repo=FakeCardRepository(_build_cards_for_sheet(1)),
            evaluator=ConstantEvaluator(score=2.0),
        )

        details = await service.start_session(user_id="u1", sheet_number=1)
        result = await service.submit_session(user_id="u1", session_id=details.session.id)

        assert result.max_score == 60.0
        assert result.total_score == 60.0
        assert result.passed is True

    async def test_time_over_forces_not_passed(self):
        repo = FakeExamRepository()
        service = ExamService(
            exam_repo=repo,
            card_repo=FakeCardRepository(_build_cards_for_sheet(1)),
            evaluator=ConstantEvaluator(score=2.0),
        )

        details = await service.start_session(user_id="u1", sheet_number=1)
        session = await repo.get_session("u1", details.session.id)
        assert session is not None
        session.started_at = datetime.now(timezone.utc) - timedelta(minutes=120)
        await repo.save_session(session)

        result = await service.submit_session(user_id="u1", session_id=details.session.id)

        assert result.total_score == 60.0
        assert result.time_over is True
        assert result.passed is False

    async def test_history_contains_only_completed_sessions(self):
        repo = FakeExamRepository()
        service = ExamService(
            exam_repo=repo,
            card_repo=FakeCardRepository(_build_cards_for_sheet(1)),
            evaluator=ConstantEvaluator(score=2.0),
        )

        session_a = await service.start_session(user_id="u1", sheet_number=1)
        await service.submit_session(user_id="u1", session_id=session_a.session.id)

        session_b = await service.start_session(user_id="u1", sheet_number=1)

        history = await service.list_history(user_id="u1")

        assert len(history) == 1
        assert history[0].session_id == session_a.session.id

        # Keep mypy/linters happy and prove second session is still in-progress.
        live = await repo.get_session("u1", session_b.session.id)
        assert live is not None
        assert live.status == ExamSessionStatus.IN_PROGRESS
