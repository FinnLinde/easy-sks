"""Integration tests for repository implementations against real PostgreSQL."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from card.db.card_repository import CardRepository
from card.model.card import Card
from card.model.card_content import CardContent
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState


@pytest.mark.asyncio
class TestCardRepository:
    async def test_save_and_get_by_id(self, db_session):
        repo = CardRepository(db_session)
        card = Card(
            card_id="test-1",
            front=CardContent(text="Question?"),
            answer=CardContent(text="Answer."),
            short_answer=["Short"],
            tags=["navigation"],
        )

        await repo.save(card)
        await db_session.flush()

        loaded = await repo.get_by_id("test-1")
        assert loaded is not None
        assert loaded.card_id == "test-1"
        assert loaded.front.text == "Question?"
        assert loaded.answer.text == "Answer."
        assert loaded.short_answer == ["Short"]
        assert loaded.tags == ["navigation"]

    async def test_get_by_id_returns_none_for_missing(self, db_session):
        repo = CardRepository(db_session)
        result = await repo.get_by_id("nonexistent")
        assert result is None

    async def test_get_by_tags(self, db_session):
        repo = CardRepository(db_session)

        card_nav = Card(
            card_id="nav-1",
            front=CardContent(text="Nav Q"),
            answer=CardContent(text="Nav A"),
            short_answer=["Nav"],
            tags=["navigation"],
        )
        card_weather = Card(
            card_id="weather-1",
            front=CardContent(text="Weather Q"),
            answer=CardContent(text="Weather A"),
            short_answer=["Weather"],
            tags=["wetterkunde"],
        )

        await repo.save(card_nav)
        await repo.save(card_weather)
        await db_session.flush()

        nav_cards = await repo.get_by_tags(["navigation"])
        assert len(nav_cards) == 1
        assert nav_cards[0].card_id == "nav-1"

    async def test_save_updates_existing(self, db_session):
        repo = CardRepository(db_session)
        card = Card(
            card_id="update-1",
            front=CardContent(text="Original"),
            answer=CardContent(text="A"),
            tags=["navigation"],
        )
        await repo.save(card)
        await db_session.flush()

        card_v2 = Card(
            card_id="update-1",
            front=CardContent(text="Updated"),
            answer=CardContent(text="A"),
            tags=["navigation"],
        )
        await repo.save(card_v2)
        await db_session.flush()

        loaded = await repo.get_by_id("update-1")
        assert loaded is not None
        assert loaded.front.text == "Updated"


@pytest.mark.asyncio
class TestSchedulingRepository:
    async def test_save_and_get_by_card_id(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        info = CardSchedulingInfo(
            card_id="sched-1",
            state=CardState.NEW,
            due=now,
        )

        await repo.save(info)
        await db_session.flush()

        loaded = await repo.get_by_card_id("sched-1")
        assert loaded is not None
        assert loaded.card_id == "sched-1"
        assert loaded.state == CardState.NEW

    async def test_get_by_card_id_returns_none_for_missing(self, db_session):
        repo = SchedulingRepository(db_session)
        result = await repo.get_by_card_id("nonexistent")
        assert result is None

    async def test_get_due(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        due_info = CardSchedulingInfo(
            card_id="due-1",
            due=now - timedelta(hours=1),
        )
        future_info = CardSchedulingInfo(
            card_id="future-1",
            due=now + timedelta(days=7),
        )

        await repo.save(due_info)
        await repo.save(future_info)
        await db_session.flush()

        due = await repo.get_due(before=now)
        card_ids = [i.card_id for i in due]
        assert "due-1" in card_ids
        assert "future-1" not in card_ids

    async def test_save_updates_existing(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        info = CardSchedulingInfo(card_id="upd-1", due=now, reps=0)
        await repo.save(info)
        await db_session.flush()

        updated = CardSchedulingInfo(card_id="upd-1", due=now, reps=5)
        await repo.save(updated)
        await db_session.flush()

        loaded = await repo.get_by_card_id("upd-1")
        assert loaded is not None
        assert loaded.reps == 5
