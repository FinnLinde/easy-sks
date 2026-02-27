"""Integration tests for repository implementations against real PostgreSQL."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from card.db.card_repository import CardRepository
from card.model.card import Card
from card.model.card_content import CardContent
from scheduling.db.review_log_table import ReviewLogRow
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog
from user.db.user_repository import UserRepository


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
    async def test_save_and_get_by_user_and_card_id(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        info = CardSchedulingInfo(
            user_id="user-1",
            card_id="sched-1",
            state=CardState.NEW,
            due=now,
        )

        await repo.save(info)
        await db_session.flush()

        loaded = await repo.get_by_user_and_card_id("user-1", "sched-1")
        assert loaded is not None
        assert loaded.card_id == "sched-1"
        assert loaded.user_id == "user-1"
        assert loaded.state == CardState.NEW

    async def test_get_by_user_and_card_id_returns_none_for_missing(self, db_session):
        repo = SchedulingRepository(db_session)
        result = await repo.get_by_user_and_card_id("user-1", "nonexistent")
        assert result is None

    async def test_get_due_for_user(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        due_info = CardSchedulingInfo(
            user_id="user-1",
            card_id="due-1",
            due=now - timedelta(hours=1),
        )
        future_info = CardSchedulingInfo(
            user_id="user-1",
            card_id="future-1",
            due=now + timedelta(days=7),
        )
        other_user_due = CardSchedulingInfo(
            user_id="user-2",
            card_id="due-2",
            due=now - timedelta(hours=1),
        )

        await repo.save(due_info)
        await repo.save(future_info)
        await repo.save(other_user_due)
        await db_session.flush()

        due = await repo.get_due_for_user(user_id="user-1", before=now)
        card_ids = [i.card_id for i in due]
        assert "due-1" in card_ids
        assert "future-1" not in card_ids
        assert "due-2" not in card_ids

    async def test_get_due_for_user_applies_deterministic_tiebreak_ordering(
        self, db_session
    ):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        same_due = now - timedelta(hours=1)
        older_review = now - timedelta(days=3)
        newer_review = now - timedelta(days=1)
        latest_due = now - timedelta(minutes=30)

        # Insert in unsorted order to prove DB retrieval ordering is explicit.
        await repo.save(CardSchedulingInfo(
            user_id="user-1",
            card_id="card-d",
            due=latest_due,
            last_review=older_review,
        ))
        await repo.save(CardSchedulingInfo(
            user_id="user-1",
            card_id="card-c",
            due=same_due,
            last_review=newer_review,
        ))
        await repo.save(CardSchedulingInfo(
            user_id="user-1",
            card_id="card-a",
            due=same_due,
            last_review=None,
        ))
        await repo.save(CardSchedulingInfo(
            user_id="user-1",
            card_id="card-b",
            due=same_due,
            last_review=None,
        ))
        await db_session.flush()

        due = await repo.get_due_for_user(user_id="user-1", before=now)
        assert [i.card_id for i in due] == ["card-a", "card-b", "card-c", "card-d"]

    async def test_save_updates_existing(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)

        info = CardSchedulingInfo(user_id="user-1", card_id="upd-1", due=now, reps=0)
        await repo.save(info)
        await db_session.flush()

        updated = CardSchedulingInfo(
            user_id="user-1", card_id="upd-1", due=now, reps=5
        )
        await repo.save(updated)
        await db_session.flush()

        loaded = await repo.get_by_user_and_card_id("user-1", "upd-1")
        assert loaded is not None
        assert loaded.reps == 5

    async def test_save_review_log(self, db_session):
        repo = SchedulingRepository(db_session)
        now = datetime.now(timezone.utc)
        log = ReviewLog(
            user_id="user-1",
            card_id="log-1",
            rating=Rating.GOOD,
            reviewed_at=now,
        )

        await repo.save_review_log(log)
        await db_session.flush()

        row = (
            await db_session.execute(
                select(ReviewLogRow).where(
                    ReviewLogRow.user_id == "user-1",
                    ReviewLogRow.card_id == "log-1",
                )
            )
        ).scalar_one()
        assert row.rating == int(Rating.GOOD)
        assert row.reviewed_at == now


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_or_create_cognito_user_creates_user(self, db_session):
        repo = UserRepository(db_session)

        user = await repo.get_or_create_cognito_user(
            cognito_sub="cognito-sub-1",
            email="captain@example.com",
        )
        await db_session.flush()

        assert user.id == "cognito-sub-1"
        assert user.auth_provider == "cognito"
        assert user.auth_provider_user_id == "cognito-sub-1"
        assert user.email == "captain@example.com"

    async def test_get_or_create_cognito_user_is_idempotent_and_updates_email(
        self, db_session
    ):
        repo = UserRepository(db_session)

        first = await repo.get_or_create_cognito_user(
            cognito_sub="cognito-sub-2",
            email=None,
        )
        second = await repo.get_or_create_cognito_user(
            cognito_sub="cognito-sub-2",
            email="updated@example.com",
        )

        assert first.id == second.id
        assert second.email == "updated@example.com"
