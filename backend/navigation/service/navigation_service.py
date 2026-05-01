"""Application service for navigation exam session lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from navigation.model.navigation_answer import NavigationAnswer
from navigation.model.navigation_result import NavigationQuestionResult, NavigationSessionResult
from navigation.model.navigation_session import (
    NavigationSession,
    NavigationSessionDetails,
    NavigationSessionHistoryItem,
    NavigationSessionQuestion,
    NavigationSessionStatus,
)
from navigation.service.navigation_evaluator_port import NavigationEvaluationRequest, NavigationEvaluatorPort
from navigation.service.navigation_repository_port import NavigationRepositoryPort

DEFAULT_TIME_LIMIT_MINUTES = 90
POINTS_PER_SHEET = 30
DEFAULT_PASS_THRESHOLD = 21.0
TOTAL_SHEETS = 10


@dataclass(frozen=True)
class NavigationTemplate:
    """Metadata for a navigation exam sheet template."""

    sheet_number: int
    display_name: str
    task_count: int
    total_points: int
    time_limit_minutes: int


class NavigationService:
    """Coordinates navigation templates, sessions, answers, and evaluations."""

    def __init__(
        self,
        repository: NavigationRepositoryPort,
        evaluator: NavigationEvaluatorPort,
        default_time_limit_minutes: int = DEFAULT_TIME_LIMIT_MINUTES,
        pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    ) -> None:
        self._repo = repository
        self._evaluator = evaluator
        self._default_time_limit_minutes = default_time_limit_minutes
        self._pass_threshold = pass_threshold

    async def list_templates(self) -> list[NavigationTemplate]:
        counts = await self._repo.count_tasks_per_sheet()
        sheets = await self._repo.get_distinct_sheet_numbers()
        return [
            NavigationTemplate(
                sheet_number=s,
                display_name=f"Navigationsaufgabe {s:02d}",
                task_count=counts.get(s, 0),
                total_points=POINTS_PER_SHEET,
                time_limit_minutes=self._default_time_limit_minutes,
            )
            for s in sheets
        ]

    async def start_session(
        self,
        sheet_number: int,
        time_limit_minutes: int | None = None,
    ) -> NavigationSessionDetails:
        tasks = await self._repo.list_tasks_for_sheet(sheet_number)
        if not tasks:
            raise ValueError(f"Navigation sheet {sheet_number} has no tasks")

        session = NavigationSession(
            sheet_number=sheet_number,
            time_limit_minutes=time_limit_minutes or self._default_time_limit_minutes,
        )
        answers = [
            NavigationAnswer(
                session_id=session.id,
                task_id=task.task_id,
                task_number=task.task_number,
            )
            for task in tasks
        ]

        await self._repo.create_session(session, answers)
        return NavigationSessionDetails(
            session=session,
            questions=[
                NavigationSessionQuestion(
                    task_number=task.task_number,
                    task=task,
                    answer=answer,
                )
                for task, answer in zip(tasks, answers, strict=False)
            ],
        )

    async def get_session_details(self, session_id: str) -> NavigationSessionDetails:
        session = await self._repo.get_session(session_id=session_id)
        if session is None:
            raise ValueError(f"Navigation session {session_id!r} not found")

        answers = await self._repo.list_answers(session.id)
        tasks = await self._repo.list_tasks_for_sheet(session.sheet_number)
        tasks_by_id = {t.task_id: t for t in tasks}

        questions: list[NavigationSessionQuestion] = []
        for answer in answers:
            task = tasks_by_id.get(answer.task_id)
            if task is None:
                continue
            questions.append(
                NavigationSessionQuestion(
                    task_number=answer.task_number,
                    task=task,
                    answer=answer,
                )
            )
        return NavigationSessionDetails(session=session, questions=questions)

    async def list_history(self) -> list[NavigationSessionHistoryItem]:
        sessions = await self._repo.list_completed_sessions()
        return [
            NavigationSessionHistoryItem(
                session_id=s.id,
                sheet_number=s.sheet_number,
                status=s.status.value,
                started_at=s.started_at,
                submitted_at=s.submitted_at,
                total_score=s.total_score,
                max_score=s.max_score,
                passed=s.passed,
                time_over=s.time_over,
            )
            for s in sessions
        ]

    async def save_answer(
        self,
        session_id: str,
        task_id: str,
        student_answer: str,
    ) -> NavigationAnswer:
        session = await self._repo.get_session(session_id=session_id)
        if session is None:
            raise ValueError(f"Navigation session {session_id!r} not found")
        if session.status != NavigationSessionStatus.IN_PROGRESS:
            raise ValueError("Navigation session is not editable")

        answer = await self._repo.get_answer(session_id=session_id, task_id=task_id)
        if answer is None:
            raise ValueError(f"Task {task_id!r} is not part of session {session_id!r}")

        answer.student_answer = student_answer
        answer.answered_at = datetime.now(timezone.utc)
        await self._repo.save_answer(answer)
        return answer

    async def submit_session(self, session_id: str) -> NavigationSessionResult:
        session = await self._repo.get_session(session_id=session_id)
        if session is None:
            raise ValueError(f"Navigation session {session_id!r} not found")

        if session.status == NavigationSessionStatus.EVALUATED:
            return await self.get_result(session_id=session_id)

        if session.status == NavigationSessionStatus.IN_PROGRESS:
            submit_time = datetime.now(timezone.utc)
            session.status = NavigationSessionStatus.SUBMITTED
            session.submitted_at = submit_time
            session.time_over = session.is_time_over(submit_time)
            await self._repo.save_session(session)

        answers = await self._repo.list_answers(session.id)
        tasks = await self._repo.list_tasks_for_sheet(session.sheet_number)
        tasks_by_id = {t.task_id: t for t in tasks}

        total_score = 0.0
        for answer in answers:
            task = tasks_by_id.get(answer.task_id)
            if task is None:
                continue

            evaluation = await self._evaluator.evaluate(
                NavigationEvaluationRequest(
                    context=task.context,
                    sub_questions=[sq.text for sq in task.sub_questions],
                    key_answers=task.key_answers,
                    solution_text=task.solution_text,
                    student_answer=answer.student_answer,
                    max_score=float(task.points),
                )
            )

            score = max(0.0, min(float(task.points), evaluation.score))
            answer.score = round(score, 1)
            answer.is_correct = evaluation.is_correct
            answer.feedback = evaluation.feedback
            total_score += answer.score
            await self._repo.save_answer(answer)

        session.status = NavigationSessionStatus.EVALUATED
        session.total_score = round(total_score, 1)
        session.max_score = float(POINTS_PER_SHEET)
        session.passed = (not session.time_over) and (total_score >= self._pass_threshold)
        await self._repo.save_session(session)

        return await self.get_result(session_id=session_id)

    async def get_result(self, session_id: str) -> NavigationSessionResult:
        details = await self.get_session_details(session_id=session_id)
        session = details.session
        if session.status != NavigationSessionStatus.EVALUATED:
            raise ValueError("Navigation result is not available yet")

        questions: list[NavigationQuestionResult] = []
        for q in details.questions:
            questions.append(
                NavigationQuestionResult(
                    task_number=q.task_number,
                    task_id=q.task.task_id,
                    context=q.task.context,
                    sub_questions=[sq.text for sq in q.task.sub_questions],
                    key_answers=q.task.key_answers,
                    solution_text=q.task.solution_text,
                    student_answer=q.answer.student_answer,
                    score=q.answer.score or 0.0,
                    max_score=float(q.task.points),
                    is_correct=bool(q.answer.is_correct),
                    feedback=q.answer.feedback or "Keine Bewertung vorhanden.",
                )
            )

        return NavigationSessionResult(
            session_id=session.id,
            sheet_number=session.sheet_number,
            status=session.status.value,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            time_limit_minutes=session.time_limit_minutes,
            time_over=session.time_over,
            total_score=session.total_score or 0.0,
            max_score=session.max_score or float(POINTS_PER_SHEET),
            passed=bool(session.passed),
            pass_score_threshold=self._pass_threshold,
            questions=questions,
        )
