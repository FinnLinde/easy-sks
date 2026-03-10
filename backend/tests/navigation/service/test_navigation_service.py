"""Unit tests for NavigationService session lifecycle logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from navigation.model.navigation_answer import NavigationAnswer
from navigation.model.navigation_session import NavigationSession, NavigationSessionStatus
from navigation.model.navigation_task import NavigationTask, SubQuestion
from navigation.service.navigation_evaluator_port import NavigationEvaluation, NavigationEvaluationRequest
from navigation.service.navigation_service import NavigationService


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


def _make_task(sheet: int, num: int, points: int = 1) -> NavigationTask:
    return NavigationTask(
        task_id=f"nav_{sheet}_{num}",
        sheet_number=sheet,
        task_number=num,
        points=points,
        context=f"Context for task {num}",
        sub_questions=[SubQuestion(text=f"Sub-question {num}", points=points)],
        solution_text=f"Solution for task {num}",
        key_answers=[f"Answer = {num * 10}° [± 1°]"],
    )


class FakeNavigationRepository:
    def __init__(self, tasks: list[NavigationTask] | None = None) -> None:
        self.tasks = tasks or []
        self.sessions: dict[str, NavigationSession] = {}
        self.answers: dict[str, list[NavigationAnswer]] = {}

    async def list_tasks_for_sheet(self, sheet_number: int) -> list[NavigationTask]:
        return [t for t in self.tasks if t.sheet_number == sheet_number]

    async def get_task(self, task_id: str) -> NavigationTask | None:
        return next((t for t in self.tasks if t.task_id == task_id), None)

    async def get_distinct_sheet_numbers(self) -> list[int]:
        return sorted({t.sheet_number for t in self.tasks})

    async def count_tasks_per_sheet(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        for t in self.tasks:
            counts[t.sheet_number] = counts.get(t.sheet_number, 0) + 1
        return counts

    async def create_session(
        self, session: NavigationSession, answers: list[NavigationAnswer]
    ) -> None:
        self.sessions[session.id] = session
        self.answers[session.id] = answers

    async def get_session(self, user_id: str, session_id: str) -> NavigationSession | None:
        s = self.sessions.get(session_id)
        if s and s.user_id == user_id:
            return s
        return None

    async def save_session(self, session: NavigationSession) -> None:
        self.sessions[session.id] = session

    async def list_answers(self, session_id: str) -> list[NavigationAnswer]:
        return self.answers.get(session_id, [])

    async def get_answer(
        self, user_id: str, session_id: str, task_id: str
    ) -> NavigationAnswer | None:
        for a in self.answers.get(session_id, []):
            if a.task_id == task_id:
                return a
        return None

    async def save_answer(self, answer: NavigationAnswer) -> None:
        answers = self.answers.get(answer.session_id, [])
        for i, a in enumerate(answers):
            if a.task_id == answer.task_id:
                answers[i] = answer
                return
        answers.append(answer)

    async def list_completed_sessions_for_user(
        self, user_id: str
    ) -> list[NavigationSession]:
        return [
            s
            for s in self.sessions.values()
            if s.user_id == user_id and s.status != NavigationSessionStatus.IN_PROGRESS
        ]


class FakeNavigationEvaluator:
    def __init__(self, score: float = 1.0, is_correct: bool = True) -> None:
        self._score = score
        self._is_correct = is_correct
        self.calls: list[NavigationEvaluationRequest] = []

    async def evaluate(self, request: NavigationEvaluationRequest) -> NavigationEvaluation:
        self.calls.append(request)
        return NavigationEvaluation(
            score=self._score,
            is_correct=self._is_correct,
            feedback="Test feedback",
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SHEET_1_TASKS = [_make_task(1, i, points=(2 if i <= 3 else 1)) for i in range(1, 7)]


@pytest.fixture
def repo() -> FakeNavigationRepository:
    return FakeNavigationRepository(tasks=list(SHEET_1_TASKS))


@pytest.fixture
def evaluator() -> FakeNavigationEvaluator:
    return FakeNavigationEvaluator()


@pytest.fixture
def service(repo, evaluator) -> NavigationService:
    return NavigationService(repository=repo, evaluator=evaluator, pass_threshold=15.0)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestListTemplates:
    async def test_returns_templates_for_available_sheets(self, service, repo):
        templates = await service.list_templates()
        assert len(templates) == 1
        assert templates[0].sheet_number == 1
        assert templates[0].task_count == 6

    async def test_returns_empty_when_no_tasks(self):
        svc = NavigationService(
            repository=FakeNavigationRepository([]),
            evaluator=FakeNavigationEvaluator(),
        )
        assert await svc.list_templates() == []


@pytest.mark.asyncio
class TestStartSession:
    async def test_creates_session_and_answers(self, service, repo):
        details = await service.start_session(user_id="u1", sheet_number=1)
        assert details.session.user_id == "u1"
        assert details.session.sheet_number == 1
        assert details.session.status == NavigationSessionStatus.IN_PROGRESS
        assert len(details.questions) == 6
        assert details.questions[0].task.task_id == "nav_1_1"

    async def test_raises_for_empty_sheet(self, service):
        with pytest.raises(ValueError, match="no tasks"):
            await service.start_session(user_id="u1", sheet_number=99)


@pytest.mark.asyncio
class TestSaveAnswer:
    async def test_saves_student_answer(self, service):
        details = await service.start_session(user_id="u1", sheet_number=1)
        sid = details.session.id
        answer = await service.save_answer(
            user_id="u1", session_id=sid, task_id="nav_1_1", student_answer="42°"
        )
        assert answer.student_answer == "42°"
        assert answer.answered_at is not None

    async def test_raises_for_wrong_task(self, service):
        details = await service.start_session(user_id="u1", sheet_number=1)
        with pytest.raises(ValueError, match="not part of session"):
            await service.save_answer(
                user_id="u1",
                session_id=details.session.id,
                task_id="nav_99_99",
                student_answer="x",
            )

    async def test_raises_for_submitted_session(self, service, repo):
        details = await service.start_session(user_id="u1", sheet_number=1)
        session = details.session
        session.status = NavigationSessionStatus.SUBMITTED
        repo.sessions[session.id] = session

        with pytest.raises(ValueError, match="not editable"):
            await service.save_answer(
                user_id="u1",
                session_id=session.id,
                task_id="nav_1_1",
                student_answer="x",
            )


@pytest.mark.asyncio
class TestSubmitSession:
    async def test_evaluates_and_scores(self, service, evaluator):
        details = await service.start_session(user_id="u1", sheet_number=1)
        result = await service.submit_session(user_id="u1", session_id=details.session.id)
        assert result.status == "evaluated"
        assert len(evaluator.calls) == 6
        assert result.total_score > 0
        assert result.passed is not None

    async def test_idempotent_on_already_evaluated(self, service, repo, evaluator):
        details = await service.start_session(user_id="u1", sheet_number=1)
        first = await service.submit_session(user_id="u1", session_id=details.session.id)
        call_count_after_first = len(evaluator.calls)
        second = await service.submit_session(user_id="u1", session_id=details.session.id)
        assert first.total_score == second.total_score
        assert len(evaluator.calls) == call_count_after_first

    async def test_time_over_prevents_passing(self, service, repo):
        details = await service.start_session(
            user_id="u1", sheet_number=1, time_limit_minutes=0
        )
        session = repo.sessions[details.session.id]
        session.started_at = datetime.now(timezone.utc) - timedelta(hours=2)

        result = await service.submit_session(user_id="u1", session_id=session.id)
        assert result.time_over is True
        assert result.passed is False

    async def test_raises_for_unknown_session(self, service):
        with pytest.raises(ValueError, match="not found"):
            await service.submit_session(user_id="u1", session_id="nonexistent")


@pytest.mark.asyncio
class TestGetResult:
    async def test_raises_before_evaluation(self, service):
        details = await service.start_session(user_id="u1", sheet_number=1)
        with pytest.raises(ValueError, match="not available"):
            await service.get_result(user_id="u1", session_id=details.session.id)


@pytest.mark.asyncio
class TestListHistory:
    async def test_returns_completed_sessions(self, service):
        details = await service.start_session(user_id="u1", sheet_number=1)
        assert await service.list_history(user_id="u1") == []

        await service.submit_session(user_id="u1", session_id=details.session.id)
        history = await service.list_history(user_id="u1")
        assert len(history) == 1
        assert history[0].session_id == details.session.id
