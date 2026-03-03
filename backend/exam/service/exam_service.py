"""Application service for exam session lifecycle orchestration."""

from __future__ import annotations

from datetime import datetime, timezone

from card.model.card import Card
from exam.model.exam_answer import ExamAnswer
from exam.model.exam_result import ExamQuestionResult, ExamSessionResult
from exam.model.exam_session import (
    ExamSession,
    ExamSessionDetails,
    ExamSessionHistoryItem,
    ExamSessionQuestion,
    ExamSessionStatus,
)
from exam.model.exam_template import ExamTemplate
from exam.service.card_repository_port import ExamCardRepositoryPort
from exam.service.exam_evaluator_port import ExamEvaluationRequest, ExamEvaluatorPort
from exam.service.exam_repository_port import ExamRepositoryPort

DEFAULT_EXAM_TIME_LIMIT_MINUTES = 90
DEFAULT_PASS_SCORE_THRESHOLD = 39.0
DEFAULT_QUESTION_MAX_SCORE = 2.0
DEFAULT_QUESTION_COUNT = 30
DEFAULT_MAX_SHEET_NUMBER = 15


class ExamService:
    """Coordinates exam templates, sessions, answers, and evaluations."""

    def __init__(
        self,
        exam_repo: ExamRepositoryPort,
        card_repo: ExamCardRepositoryPort,
        evaluator: ExamEvaluatorPort,
        default_time_limit_minutes: int = DEFAULT_EXAM_TIME_LIMIT_MINUTES,
        pass_score_threshold: float = DEFAULT_PASS_SCORE_THRESHOLD,
        question_max_score: float = DEFAULT_QUESTION_MAX_SCORE,
        question_count: int = DEFAULT_QUESTION_COUNT,
        max_sheet_number: int = DEFAULT_MAX_SHEET_NUMBER,
    ) -> None:
        self._exam_repo = exam_repo
        self._card_repo = card_repo
        self._evaluator = evaluator
        self._default_time_limit_minutes = default_time_limit_minutes
        self._pass_score_threshold = pass_score_threshold
        self._question_max_score = question_max_score
        self._question_count = question_count
        self._max_sheet_number = max_sheet_number

    @property
    def pass_score_threshold(self) -> float:
        return self._pass_score_threshold

    @property
    def question_max_score(self) -> float:
        return self._question_max_score

    async def list_templates(self) -> list[ExamTemplate]:
        cards = await self._card_repo.list_all()
        question_count_by_sheet: dict[int, int] = {
            number: 0 for number in range(1, self._max_sheet_number + 1)
        }

        for card in cards:
            for sheet in card.exam_sheets:
                if 1 <= sheet <= self._max_sheet_number:
                    question_count_by_sheet[sheet] += 1

        return [
            ExamTemplate(
                sheet_number=sheet_number,
                display_name=f"Pruefungsbogen {sheet_number}",
                question_count=question_count_by_sheet[sheet_number],
                time_limit_minutes=self._default_time_limit_minutes,
            )
            for sheet_number in range(1, self._max_sheet_number + 1)
        ]

    async def start_session(
        self,
        user_id: str,
        sheet_number: int,
        time_limit_minutes: int | None = None,
    ) -> ExamSessionDetails:
        if sheet_number < 1 or sheet_number > self._max_sheet_number:
            raise ValueError(f"Unsupported exam sheet: {sheet_number}")

        cards = await self._get_cards_for_sheet(sheet_number)
        if len(cards) != self._question_count:
            raise ValueError(
                f"Exam sheet {sheet_number} has {len(cards)} questions; expected {self._question_count}"
            )

        session = ExamSession(
            user_id=user_id,
            sheet_number=sheet_number,
            time_limit_minutes=time_limit_minutes or self._default_time_limit_minutes,
        )
        answers = [
            ExamAnswer(
                session_id=session.id,
                card_id=card.card_id,
                question_number=index + 1,
            )
            for index, card in enumerate(cards)
        ]

        await self._exam_repo.create_session(session, answers)
        return ExamSessionDetails(
            session=session,
            questions=[
                ExamSessionQuestion(
                    question_number=answer.question_number,
                    card=card,
                    answer=answer,
                )
                for answer, card in zip(answers, cards, strict=False)
            ],
        )

    async def list_history(self, user_id: str) -> list[ExamSessionHistoryItem]:
        sessions = await self._exam_repo.list_completed_sessions_for_user(user_id)
        return [
            ExamSessionHistoryItem(
                session_id=session.id,
                sheet_number=session.sheet_number,
                status=session.status.value,
                started_at=session.started_at,
                submitted_at=session.submitted_at,
                total_score=session.total_score,
                max_score=session.max_score,
                passed=session.passed,
                time_over=session.time_over,
            )
            for session in sessions
        ]

    async def get_session_details(self, user_id: str, session_id: str) -> ExamSessionDetails:
        session = await self._exam_repo.get_session(user_id=user_id, session_id=session_id)
        if session is None:
            raise ValueError(f"Exam session {session_id!r} not found")

        answers = await self._exam_repo.list_answers(session.id)
        cards = await self._card_repo.list_all()
        cards_by_id = {card.card_id: card for card in cards}

        questions: list[ExamSessionQuestion] = []
        for answer in answers:
            card = cards_by_id.get(answer.card_id)
            if card is None:
                continue
            questions.append(
                ExamSessionQuestion(
                    question_number=answer.question_number,
                    card=card,
                    answer=answer,
                )
            )

        return ExamSessionDetails(session=session, questions=questions)

    async def save_answer(
        self,
        user_id: str,
        session_id: str,
        card_id: str,
        student_answer: str,
    ) -> ExamAnswer:
        session = await self._exam_repo.get_session(user_id=user_id, session_id=session_id)
        if session is None:
            raise ValueError(f"Exam session {session_id!r} not found")
        if session.status != ExamSessionStatus.IN_PROGRESS:
            raise ValueError("Exam session is not editable")

        answer = await self._exam_repo.get_answer(
            user_id=user_id,
            session_id=session_id,
            card_id=card_id,
        )
        if answer is None:
            raise ValueError(f"Card {card_id!r} is not part of session {session_id!r}")

        answer.student_answer = student_answer
        answer.answered_at = datetime.now(timezone.utc)

        await self._exam_repo.save_answer(answer)
        return answer

    async def submit_session(self, user_id: str, session_id: str) -> ExamSessionResult:
        session = await self._exam_repo.get_session(user_id=user_id, session_id=session_id)
        if session is None:
            raise ValueError(f"Exam session {session_id!r} not found")

        if session.status == ExamSessionStatus.EVALUATED:
            return await self.get_result(user_id=user_id, session_id=session_id)

        if session.status == ExamSessionStatus.IN_PROGRESS:
            submit_time = datetime.now(timezone.utc)
            session.status = ExamSessionStatus.SUBMITTED
            session.submitted_at = submit_time
            session.time_over = session.is_time_over(submit_time)
            await self._exam_repo.save_session(session)

        answers = await self._exam_repo.list_answers(session.id)
        total_score = 0.0

        for answer in answers:
            card = await self._card_repo.get_by_id(answer.card_id)
            if card is None:
                continue

            evaluation = await self._evaluator.evaluate(
                ExamEvaluationRequest(
                    question_text=card.front.text,
                    short_answer=card.short_answer,
                    reference_answer=card.answer.text,
                    student_answer=answer.student_answer,
                    max_score=self._question_max_score,
                )
            )

            score = max(0.0, min(self._question_max_score, evaluation.score))
            answer.score = float(round(score))
            answer.is_correct = evaluation.is_correct
            answer.feedback = evaluation.feedback
            answer.errors = evaluation.errors
            total_score += answer.score

            await self._exam_repo.save_answer(answer)

        max_score = len(answers) * self._question_max_score
        session.status = ExamSessionStatus.EVALUATED
        session.total_score = round(total_score, 2)
        session.max_score = max_score
        session.passed = (not session.time_over) and (total_score >= self._pass_score_threshold)
        await self._exam_repo.save_session(session)

        return await self.get_result(user_id=user_id, session_id=session_id)

    async def get_result(self, user_id: str, session_id: str) -> ExamSessionResult:
        details = await self.get_session_details(user_id=user_id, session_id=session_id)
        session = details.session
        if session.status != ExamSessionStatus.EVALUATED:
            raise ValueError("Exam result is not available yet")

        questions: list[ExamQuestionResult] = []
        for question in details.questions:
            answer = question.answer
            questions.append(
                ExamQuestionResult(
                    question_number=question.question_number,
                    card_id=question.card.card_id,
                    question_text=question.card.front.text,
                    reference_short_answer=question.card.short_answer,
                    student_answer=answer.student_answer,
                    score=answer.score or 0.0,
                    is_correct=bool(answer.is_correct),
                    feedback=answer.feedback or "Keine Bewertung vorhanden.",
                    errors=answer.errors,
                )
            )

        return ExamSessionResult(
            session_id=session.id,
            sheet_number=session.sheet_number,
            status=session.status.value,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            time_limit_minutes=session.time_limit_minutes,
            time_over=session.time_over,
            total_score=session.total_score or 0.0,
            max_score=session.max_score or len(questions) * self._question_max_score,
            passed=bool(session.passed),
            pass_score_threshold=self._pass_score_threshold,
            questions=questions,
        )

    async def _get_cards_for_sheet(self, sheet_number: int) -> list[Card]:
        cards = await self._card_repo.list_all()
        matches = [card for card in cards if sheet_number in card.exam_sheets]
        matches.sort(key=lambda card: card.card_id)
        return matches
