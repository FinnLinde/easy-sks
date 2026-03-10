"""Integration tests for navigation exam endpoints."""

from __future__ import annotations

import pytest

from navigation.controller.navigation_controller import get_navigation_service
from navigation.db.navigation_repository import NavigationRepository
from navigation.db.navigation_tables import NavigationTaskRow
from navigation.service.heuristic_navigation_evaluator import HeuristicNavigationEvaluator
from navigation.service.navigation_service import NavigationService
from main import app
from user.db.user_table import UserRow


async def _seed_tasks(db_session, sheet: int = 1, count: int = 3) -> None:
    """Insert a minimal set of navigation tasks for testing."""
    for i in range(1, count + 1):
        db_session.add(
            NavigationTaskRow(
                task_id=f"nav_{sheet}_{i}",
                sheet_number=sheet,
                task_number=i,
                points=2 if i <= 2 else 1,
                context=f"Test context for task {i}",
                sub_questions=[{"text": f"Sub-question {i}", "points": 1}],
                solution_text=f"Solution {i}",
                key_answers=[f"Answer = {i * 10}° [± 1°]"],
            )
        )
    await db_session.flush()


async def _add_user(db_session, user_id: str = "test-user") -> None:
    db_session.add(
        UserRow(
            id=user_id,
            auth_provider="cognito",
            auth_provider_user_id=user_id,
            email=f"{user_id}@example.com",
        )
    )
    await db_session.flush()


def _override_service(db_session):
    """Wire a real NavigationService backed by the test DB session."""
    service = NavigationService(
        repository=NavigationRepository(db_session),
        evaluator=HeuristicNavigationEvaluator(),
        pass_threshold=3.0,
    )
    original = app.dependency_overrides.get(get_navigation_service)
    app.dependency_overrides[get_navigation_service] = lambda: service
    return original


def _restore_override(original):
    if original is None:
        app.dependency_overrides.pop(get_navigation_service, None)
    else:
        app.dependency_overrides[get_navigation_service] = original


@pytest.mark.asyncio
class TestNavigationApi:
    async def test_list_templates_returns_seeded_sheets(self, client, db_session):
        await _seed_tasks(db_session, sheet=1, count=3)
        await _seed_tasks(db_session, sheet=2, count=2)
        original = _override_service(db_session)
        try:
            resp = await client.get("/navigation-exams")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 2
            assert data[0]["sheet_number"] == 1
            assert data[0]["task_count"] == 3
            assert data[1]["sheet_number"] == 2
            assert data[1]["task_count"] == 2
        finally:
            _restore_override(original)

    async def test_start_session_creates_answers(self, client, db_session):
        await _add_user(db_session)
        await _seed_tasks(db_session, sheet=1, count=3)
        original = _override_service(db_session)
        try:
            resp = await client.post(
                "/navigation-sessions",
                json={"sheet_number": 1},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["sheet_number"] == 1
            assert data["status"] == "in_progress"
            assert data["task_count"] == 3
            assert len(data["questions"]) == 3
            assert data["questions"][0]["task_id"] == "nav_1_1"
            assert data["questions"][0]["points"] == 2
        finally:
            _restore_override(original)

    async def test_start_session_fails_for_empty_sheet(self, client, db_session):
        await _add_user(db_session)
        original = _override_service(db_session)
        try:
            resp = await client.post(
                "/navigation-sessions",
                json={"sheet_number": 9},
            )
            assert resp.status_code == 400
        finally:
            _restore_override(original)

    async def test_save_and_retrieve_answer(self, client, db_session):
        await _add_user(db_session)
        await _seed_tasks(db_session, sheet=1, count=3)
        original = _override_service(db_session)
        try:
            start_resp = await client.post(
                "/navigation-sessions", json={"sheet_number": 1}
            )
            session_id = start_resp.json()["session_id"]

            save_resp = await client.put(
                f"/navigation-sessions/{session_id}/answers/nav_1_1",
                json={"student_answer": "KaK = 286°"},
            )
            assert save_resp.status_code == 200
            assert save_resp.json()["student_answer"] == "KaK = 286°"

            get_resp = await client.get(f"/navigation-sessions/{session_id}")
            assert get_resp.status_code == 200
            questions = get_resp.json()["questions"]
            q1 = next(q for q in questions if q["task_id"] == "nav_1_1")
            assert q1["student_answer"] == "KaK = 286°"
        finally:
            _restore_override(original)

    async def test_submit_evaluates_and_returns_result(self, client, db_session):
        await _add_user(db_session)
        await _seed_tasks(db_session, sheet=1, count=3)
        original = _override_service(db_session)
        try:
            start_resp = await client.post(
                "/navigation-sessions", json={"sheet_number": 1}
            )
            session_id = start_resp.json()["session_id"]

            await client.put(
                f"/navigation-sessions/{session_id}/answers/nav_1_1",
                json={"student_answer": "Answer = 10°"},
            )

            submit_resp = await client.post(
                f"/navigation-sessions/{session_id}/submit"
            )
            assert submit_resp.status_code == 200
            result = submit_resp.json()
            assert result["status"] == "evaluated"
            assert result["max_score"] == 30.0
            assert isinstance(result["total_score"], (int, float))
            assert isinstance(result["passed"], bool)
            assert len(result["questions"]) == 3

            result_resp = await client.get(
                f"/navigation-sessions/{session_id}/result"
            )
            assert result_resp.status_code == 200
            assert result_resp.json()["session_id"] == session_id
        finally:
            _restore_override(original)

    async def test_history_shows_evaluated_sessions(self, client, db_session):
        await _add_user(db_session)
        await _seed_tasks(db_session, sheet=1, count=3)
        original = _override_service(db_session)
        try:
            history_before = await client.get("/navigation-sessions")
            assert history_before.json() == []

            start_resp = await client.post(
                "/navigation-sessions", json={"sheet_number": 1}
            )
            session_id = start_resp.json()["session_id"]
            await client.post(f"/navigation-sessions/{session_id}/submit")

            history_after = await client.get("/navigation-sessions")
            assert history_after.status_code == 200
            assert len(history_after.json()) == 1
            assert history_after.json()[0]["session_id"] == session_id
        finally:
            _restore_override(original)
