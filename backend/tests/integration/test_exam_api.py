"""Integration tests for exam simulation API endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from card.db.card_table import CardRow
from exam.db.exam_tables import ExamSessionRow
from user.db.user_table import UserRow


async def _add_user(db_session, user_id: str) -> None:
    db_session.add(
        UserRow(
            id=user_id,
            auth_provider="cognito",
            auth_provider_user_id=user_id,
            email=f"{user_id}@example.com",
        )
    )
    await db_session.flush()


async def _seed_sheet_cards(db_session, sheet_number: int, count: int = 30) -> None:
    for index in range(count):
        db_session.add(
            CardRow(
                card_id=f"exam-{sheet_number}-{index:02d}",
                front_text=f"Frage {index}",
                front_images=[],
                answer_text="Referenzantwort alpha beta",
                answer_images=[],
                short_answer=["alpha", "beta"],
                tags=["navigation"],
                exam_sheets=[sheet_number],
            )
        )
    await db_session.flush()


@pytest.mark.asyncio
class TestExamApi:
    async def test_lists_exam_templates(self, client, db_session):
        await _add_user(db_session, "test-user")
        await _seed_sheet_cards(db_session, sheet_number=1, count=30)

        resp = await client.get("/exams")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 15
        assert data[0]["sheet_number"] == 1
        assert data[0]["question_count"] == 30

    async def test_full_flow_with_history_and_result(self, client, db_session):
        await _add_user(db_session, "test-user")
        await _seed_sheet_cards(db_session, sheet_number=1, count=30)

        start = await client.post("/exam-sessions", json={"sheet_number": 1})
        assert start.status_code == 200
        started = start.json()
        session_id = started["session_id"]
        first_card_id = started["questions"][0]["card_id"]

        save = await client.put(
            f"/exam-sessions/{session_id}/answers/{first_card_id}",
            json={"student_answer": "alpha und beta"},
        )
        assert save.status_code == 200

        await db_session.execute(
            update(ExamSessionRow)
            .where(ExamSessionRow.id == session_id)
            .values(started_at=datetime.now(timezone.utc) - timedelta(minutes=91))
        )
        await db_session.flush()

        submit = await client.post(f"/exam-sessions/{session_id}/submit")
        assert submit.status_code == 200
        result = submit.json()
        assert result["session_id"] == session_id
        assert result["status"] == "evaluated"
        assert result["time_over"] is True
        assert result["passed"] is False
        assert result["max_score"] == 60.0
        assert len(result["questions"]) == 30

        history = await client.get("/exam-sessions")
        assert history.status_code == 200
        history_items = history.json()
        assert len(history_items) == 1
        assert history_items[0]["session_id"] == session_id

        fetched_result = await client.get(f"/exam-sessions/{session_id}/result")
        assert fetched_result.status_code == 200
        assert fetched_result.json()["session_id"] == session_id

    async def test_rejects_start_when_sheet_has_not_30_questions(self, client, db_session):
        await _add_user(db_session, "test-user")
        await _seed_sheet_cards(db_session, sheet_number=1, count=29)

        resp = await client.post("/exam-sessions", json={"sheet_number": 1})

        assert resp.status_code == 400
        assert "expected 30" in resp.json()["detail"]

    async def test_cannot_edit_answer_after_submit(self, client, db_session):
        await _add_user(db_session, "test-user")
        await _seed_sheet_cards(db_session, sheet_number=1, count=30)

        start = await client.post("/exam-sessions", json={"sheet_number": 1})
        started = start.json()
        session_id = started["session_id"]
        first_card_id = started["questions"][0]["card_id"]

        submit = await client.post(f"/exam-sessions/{session_id}/submit")
        assert submit.status_code == 200

        save_after_submit = await client.put(
            f"/exam-sessions/{session_id}/answers/{first_card_id}",
            json={"student_answer": "neue Antwort"},
        )
        assert save_after_submit.status_code == 400
        assert save_after_submit.json()["detail"] == "Exam session is not editable"
