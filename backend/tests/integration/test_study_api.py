"""Integration tests for the study API endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from card.db.card_table import CardRow
from scheduling.db.scheduling_table import CardSchedulingInfoRow
from user.db.user_table import UserRow


@pytest.mark.asyncio
class TestTopicsEndpoint:
    async def test_list_topics(self, client):
        resp = await client.get("/topics")
        assert resp.status_code == 200
        topics = resp.json()
        assert len(topics) == 5
        values = {t["value"] for t in topics}
        assert "navigation" in values
        assert "wetterkunde" in values


@pytest.mark.asyncio
class TestDueCardsEndpoint:
    async def test_provisions_local_user_on_authenticated_request(
        self, client, db_session
    ):
        resp = await client.get("/study/due")
        assert resp.status_code == 200

        user = await db_session.get(UserRow, "test-user")
        assert user is not None
        assert user.auth_provider == "cognito"
        assert user.auth_provider_user_id == "test-user"

    async def test_returns_due_cards(self, client, db_session):
        now = datetime.now(timezone.utc)
        db_session.add(CardRow(
            card_id="api-due-1",
            front_text="Question?",
            front_images=[],
            answer_text="Answer.",
            answer_images=[],
            short_answer=["Short"],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-due-1",
            state=0,
            stability=0.0,
            difficulty=0.0,
            elapsed_days=0,
            scheduled_days=0,
            reps=0,
            lapses=0,
            due=now - timedelta(hours=1),
            last_review=None,
        ))
        await db_session.flush()

        resp = await client.get("/study/due")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        card_ids = [sc["card"]["card_id"] for sc in data]
        assert "api-due-1" in card_ids

    async def test_filters_by_topic(self, client, db_session):
        now = datetime.now(timezone.utc)
        db_session.add(CardRow(
            card_id="api-nav-1",
            front_text="Nav Q",
            front_images=[],
            answer_text="Nav A",
            answer_images=[],
            short_answer=[],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-nav-1",
            state=0, stability=0, difficulty=0,
            elapsed_days=0, scheduled_days=0,
            reps=0, lapses=0,
            due=now - timedelta(hours=1),
        ))
        db_session.add(CardRow(
            card_id="api-weather-1",
            front_text="Weather Q",
            front_images=[],
            answer_text="Weather A",
            answer_images=[],
            short_answer=[],
            tags=["wetterkunde"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-weather-1",
            state=0, stability=0, difficulty=0,
            elapsed_days=0, scheduled_days=0,
            reps=0, lapses=0,
            due=now - timedelta(hours=1),
        ))
        await db_session.flush()

        resp = await client.get("/study/due?topic=navigation")
        assert resp.status_code == 200
        data = resp.json()
        card_ids = [sc["card"]["card_id"] for sc in data]
        assert "api-nav-1" in card_ids
        assert "api-weather-1" not in card_ids

    async def test_excludes_due_cards_of_other_users(self, client, db_session):
        now = datetime.now(timezone.utc)
        # Fill the queue cap with own due cards so no "new introductions"
        # are added and we can assert strict user isolation of due data.
        for i in range(20):
            card_id = f"api-own-{i}"
            db_session.add(CardRow(
                card_id=card_id,
                front_text="Own Q",
                front_images=[],
                answer_text="Own A",
                answer_images=[],
                short_answer=[],
                tags=["navigation"],
            ))
            db_session.add(CardSchedulingInfoRow(
                user_id="test-user",
                card_id=card_id,
                state=0, stability=0, difficulty=0,
                elapsed_days=0, scheduled_days=0,
                reps=0, lapses=0,
                due=now - timedelta(hours=1),
            ))
        db_session.add(CardRow(
            card_id="api-other-1",
            front_text="Other Q",
            front_images=[],
            answer_text="Other A",
            answer_images=[],
            short_answer=[],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="other-user",
            card_id="api-other-1",
            state=0, stability=0, difficulty=0,
            elapsed_days=0, scheduled_days=0,
            reps=0, lapses=0,
            due=now - timedelta(hours=1),
        ))
        await db_session.flush()

        resp = await client.get("/study/due")
        assert resp.status_code == 200
        data = resp.json()
        card_ids = [sc["card"]["card_id"] for sc in data]
        assert "api-own-0" in card_ids
        assert "api-other-1" not in card_ids

    async def test_invalid_topic_returns_400(self, client):
        resp = await client.get("/study/due?topic=invalid_topic")
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestReviewEndpoint:
    async def test_review_updates_scheduling(self, client, db_session):
        now = datetime.now(timezone.utc)
        db_session.add(CardRow(
            card_id="api-review-1",
            front_text="Q",
            front_images=[],
            answer_text="A",
            answer_images=[],
            short_answer=["S"],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-review-1",
            state=0, stability=0, difficulty=0,
            elapsed_days=0, scheduled_days=0,
            reps=0, lapses=0,
            due=now - timedelta(hours=1),
        ))
        await db_session.flush()

        resp = await client.post("/study/review", json={
            "card_id": "api-review-1",
            "rating": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["card"]["card_id"] == "api-review-1"
        assert data["scheduling_info"]["reps"] == 1

    async def test_review_missing_card_returns_404(self, client):
        resp = await client.post("/study/review", json={
            "card_id": "nonexistent",
            "rating": 3,
        })
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestPracticeCardsEndpoint:
    async def test_returns_future_cards_when_no_due_cards_exist(self, client, db_session):
        now = datetime.now(timezone.utc)
        db_session.add(CardRow(
            card_id="api-practice-1",
            front_text="Practice Q",
            front_images=[],
            answer_text="Practice A",
            answer_images=[],
            short_answer=["Short"],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-practice-1",
            state=0,
            stability=0.0,
            difficulty=0.0,
            elapsed_days=0,
            scheduled_days=0,
            reps=0,
            lapses=0,
            due=now + timedelta(days=3),
            last_review=None,
        ))
        await db_session.flush()

        resp = await client.get("/study/practice")
        assert resp.status_code == 200
        data = resp.json()
        card_ids = [sc["card"]["card_id"] for sc in data]
        assert "api-practice-1" in card_ids

    async def test_invalid_topic_returns_400(self, client):
        resp = await client.get("/study/practice?topic=invalid_topic")
        assert resp.status_code == 400

    async def test_practice_review_updates_scheduling_state(
        self, client, db_session
    ):
        now = datetime.now(timezone.utc)
        db_session.add(CardRow(
            card_id="api-practice-review-1",
            front_text="Practice review Q",
            front_images=[],
            answer_text="Practice review A",
            answer_images=[],
            short_answer=["Short"],
            tags=["navigation"],
        ))
        db_session.add(CardSchedulingInfoRow(
            user_id="test-user",
            card_id="api-practice-review-1",
            state=0,
            stability=0.0,
            difficulty=0.0,
            elapsed_days=0,
            scheduled_days=0,
            reps=0,
            lapses=0,
            due=now + timedelta(days=2),
            last_review=None,
        ))
        await db_session.flush()

        practice_resp = await client.get("/study/practice")
        assert practice_resp.status_code == 200
        practice_ids = [sc["card"]["card_id"] for sc in practice_resp.json()]
        assert "api-practice-review-1" in practice_ids

        review_resp = await client.post("/study/review", json={
            "card_id": "api-practice-review-1",
            "rating": 3,
        })
        assert review_resp.status_code == 200
        reviewed = review_resp.json()
        assert reviewed["card"]["card_id"] == "api-practice-review-1"
        assert reviewed["scheduling_info"]["reps"] == 1


@pytest.mark.asyncio
class TestCardEndpoint:
    async def test_get_card_by_id(self, client, db_session):
        db_session.add(CardRow(
            card_id="api-card-1",
            front_text="Front text",
            front_images=[],
            answer_text="Answer text",
            answer_images=[],
            short_answer=["Bullet 1", "Bullet 2"],
            tags=["wetterkunde"],
        ))
        await db_session.flush()

        resp = await client.get("/cards/api-card-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["card_id"] == "api-card-1"
        assert data["front"]["text"] == "Front text"
        assert data["short_answer"] == ["Bullet 1", "Bullet 2"]
        assert data["tags"] == ["wetterkunde"]

    async def test_get_missing_card_returns_404(self, client):
        resp = await client.get("/cards/nonexistent")
        assert resp.status_code == 404
