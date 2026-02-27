from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from card.model.card import Card
from card.model.card_content import CardContent
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog
from scheduling.service.scheduling_service import SchedulingService

from study.model.sks_topic import SksTopic
from study.service.study_service import StudyService


# -- Fake implementations of the ports ------------------------------------


class FakeCardRepository:
    def __init__(self, cards: list[Card] | None = None) -> None:
        self._cards = {c.card_id: c for c in (cards or [])}

    async def list_all(self) -> list[Card]:
        return list(self._cards.values())

    async def get_by_id(self, card_id: str) -> Card | None:
        return self._cards.get(card_id)

    async def get_by_tags(self, tags: list[str]) -> list[Card]:
        return [
            c for c in self._cards.values()
            if any(t in c.tags for t in tags)
        ]


class FakeSchedulingRepository:
    def __init__(self, infos: list[CardSchedulingInfo] | None = None) -> None:
        self._infos = {(i.user_id, i.card_id): i for i in (infos or [])}
        self.saved_review_logs: list[ReviewLog] = []

    async def list_for_user(self, user_id: str) -> list[CardSchedulingInfo]:
        return [i for i in self._infos.values() if i.user_id == user_id]

    async def get_by_user_and_card_id(
        self, user_id: str, card_id: str
    ) -> CardSchedulingInfo | None:
        return self._infos.get((user_id, card_id))

    async def get_due_for_user(
        self, user_id: str, before: datetime
    ) -> list[CardSchedulingInfo]:
        return [
            i
            for i in self._infos.values()
            if i.user_id == user_id and i.due <= before
        ]

    async def save(self, info: CardSchedulingInfo) -> None:
        self._infos[(info.user_id, info.card_id)] = info

    async def save_review_log(self, log: ReviewLog) -> None:
        self.saved_review_logs.append(log)


class FailingReviewLogRepository(FakeSchedulingRepository):
    async def save_review_log(self, log: ReviewLog) -> None:
        raise RuntimeError("simulated review log failure")


# -- Helpers ---------------------------------------------------------------


def _make_card(card_id: str, tags: list[str]) -> Card:
    return Card(
        card_id=card_id,
        front=CardContent(text=f"Question for {card_id}"),
        answer=CardContent(text="Answer"),
        short_answer=["Short"],
        tags=tags,
    )


def _make_due_info(card_id: str) -> CardSchedulingInfo:
    """Create a scheduling info that is already due."""
    return CardSchedulingInfo(
        user_id="test-user",
        card_id=card_id,
        due=datetime.now(timezone.utc) - timedelta(hours=1),
    )


def _make_future_info(card_id: str) -> CardSchedulingInfo:
    """Create a scheduling info that is not yet due."""
    return CardSchedulingInfo(
        user_id="test-user",
        card_id=card_id,
        due=datetime.now(timezone.utc) + timedelta(days=7),
    )


# -- Tests -----------------------------------------------------------------


class TestGetDueCards:
    @pytest.mark.asyncio
    async def test_returns_due_cards(self):
        card = _make_card("c1", ["navigation"])
        info = _make_due_info("c1")

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([info]),
            scheduling_service=SchedulingService(),
        )

        result = await service.get_due_cards(user_id="test-user")

        assert len(result) == 1
        assert result[0].card.card_id == "c1"

    @pytest.mark.asyncio
    async def test_excludes_future_cards(self):
        card = _make_card("c1", ["navigation"])
        info = _make_future_info("c1")

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([info]),
            scheduling_service=SchedulingService(),
        )

        result = await service.get_due_cards(user_id="test-user")

        assert result == []

    @pytest.mark.asyncio
    async def test_filters_by_topic(self):
        nav_card = _make_card("c1", ["navigation"])
        weather_card = _make_card("c2", ["wetterkunde"])

        service = StudyService(
            card_repo=FakeCardRepository([nav_card, weather_card]),
            scheduling_repo=FakeSchedulingRepository([
                _make_due_info("c1"),
                _make_due_info("c2"),
            ]),
            scheduling_service=SchedulingService(),
        )

        result = await service.get_due_cards(
            user_id="test-user", topic=SksTopic.NAVIGATION
        )

        assert len(result) == 1
        assert result[0].card.card_id == "c1"

    @pytest.mark.asyncio
    async def test_returns_all_topics_when_no_filter(self):
        cards = [
            _make_card("c1", ["navigation"]),
            _make_card("c2", ["wetterkunde"]),
            _make_card("c3", ["seemannschaft_i"]),
        ]
        infos = [_make_due_info(c.card_id) for c in cards]

        service = StudyService(
            card_repo=FakeCardRepository(cards),
            scheduling_repo=FakeSchedulingRepository(infos),
            scheduling_service=SchedulingService(),
        )

        result = await service.get_due_cards(user_id="test-user")

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_skips_scheduling_info_without_matching_card(self):
        info = _make_due_info("orphan-id")

        service = StudyService(
            card_repo=FakeCardRepository([]),
            scheduling_repo=FakeSchedulingRepository([info]),
            scheduling_service=SchedulingService(),
        )

        result = await service.get_due_cards(user_id="test-user")

        assert result == []

    @pytest.mark.asyncio
    async def test_preserves_due_order_from_repository(self):
        first = _make_card("first", ["navigation"])
        second = _make_card("second", ["navigation"])

        # Repository order is authoritative for due queue sequencing.
        service = StudyService(
            card_repo=FakeCardRepository([first, second]),
            scheduling_repo=FakeSchedulingRepository([
                _make_due_info("second"),
                _make_due_info("first"),
            ]),
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=2,
        )

        result = await service.get_due_cards(user_id="test-user")

        assert [sc.card.card_id for sc in result] == ["second", "first"]

    @pytest.mark.asyncio
    async def test_bootstraps_initial_due_queue_for_new_user(self):
        cards = [
            _make_card("c1", ["navigation"]),
            _make_card("c2", ["wetterkunde"]),
            _make_card("c3", ["seemannschaft_i"]),
        ]
        sched_repo = FakeSchedulingRepository([])

        service = StudyService(
            card_repo=FakeCardRepository(cards),
            scheduling_repo=sched_repo,
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=2,
        )

        result = await service.get_due_cards(user_id="test-user")

        assert [sc.card.card_id for sc in result] == ["c1", "c2"]

        saved_c1 = await sched_repo.get_by_user_and_card_id("test-user", "c1")
        saved_c2 = await sched_repo.get_by_user_and_card_id("test-user", "c2")
        saved_c3 = await sched_repo.get_by_user_and_card_id("test-user", "c3")
        assert saved_c1 is not None
        assert saved_c2 is not None
        assert saved_c3 is None

    @pytest.mark.asyncio
    async def test_prioritizes_due_cards_before_introducing_new_cards(self):
        due_card = _make_card("due-1", ["navigation"])
        new_card = _make_card("new-1", ["navigation"])
        sched_repo = FakeSchedulingRepository([_make_due_info("due-1")])

        service = StudyService(
            card_repo=FakeCardRepository([due_card, new_card]),
            scheduling_repo=sched_repo,
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=2,
        )

        result = await service.get_due_cards(user_id="test-user")

        assert [sc.card.card_id for sc in result] == ["due-1", "new-1"]

    @pytest.mark.asyncio
    async def test_topic_filter_only_introduces_matching_new_cards(self):
        nav_1 = _make_card("nav-1", ["navigation"])
        nav_2 = _make_card("nav-2", ["navigation"])
        weather = _make_card("wx-1", ["wetterkunde"])

        service = StudyService(
            card_repo=FakeCardRepository([nav_1, nav_2, weather]),
            scheduling_repo=FakeSchedulingRepository([]),
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=5,
        )

        result = await service.get_due_cards(
            user_id="test-user",
            topic=SksTopic.NAVIGATION,
        )

        assert [sc.card.card_id for sc in result] == ["nav-1", "nav-2"]


class TestReviewCard:
    @pytest.mark.asyncio
    async def test_returns_updated_study_card(self):
        card = _make_card("c1", ["navigation"])
        info = CardSchedulingInfo(user_id="test-user", card_id="c1")

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([info]),
            scheduling_service=SchedulingService(),
        )

        result = await service.review_card("test-user", "c1", Rating.GOOD)

        assert result.card.card_id == "c1"
        assert result.scheduling_info.reps == 1

    @pytest.mark.asyncio
    async def test_persists_updated_scheduling_info(self):
        card = _make_card("c1", ["navigation"])
        info = CardSchedulingInfo(user_id="test-user", card_id="c1")
        sched_repo = FakeSchedulingRepository([info])

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=sched_repo,
            scheduling_service=SchedulingService(),
        )

        await service.review_card("test-user", "c1", Rating.GOOD)

        saved = await sched_repo.get_by_user_and_card_id("test-user", "c1")
        assert saved is not None
        assert saved.reps == 1
        assert saved.stability > 0.0

    @pytest.mark.asyncio
    async def test_persists_review_log(self):
        card = _make_card("c1", ["navigation"])
        info = CardSchedulingInfo(user_id="test-user", card_id="c1")
        sched_repo = FakeSchedulingRepository([info])

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=sched_repo,
            scheduling_service=SchedulingService(),
        )

        await service.review_card("test-user", "c1", Rating.GOOD)

        assert len(sched_repo.saved_review_logs) == 1
        saved_log = sched_repo.saved_review_logs[0]
        assert saved_log.user_id == "test-user"
        assert saved_log.card_id == "c1"
        assert saved_log.rating == Rating.GOOD

    @pytest.mark.asyncio
    async def test_raises_for_missing_scheduling_info(self):
        card = _make_card("c1", ["navigation"])

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([]),
            scheduling_service=SchedulingService(),
        )

        with pytest.raises(ValueError, match="No scheduling info"):
            await service.review_card("test-user", "c1", Rating.GOOD)

    @pytest.mark.asyncio
    async def test_raises_for_missing_card(self):
        info = CardSchedulingInfo(user_id="test-user", card_id="c1")

        service = StudyService(
            card_repo=FakeCardRepository([]),
            scheduling_repo=FakeSchedulingRepository([info]),
            scheduling_service=SchedulingService(),
        )

        with pytest.raises(ValueError, match="not found"):
            await service.review_card("test-user", "c1", Rating.GOOD)

    @pytest.mark.asyncio
    async def test_raises_when_review_log_persistence_fails(self):
        card = _make_card("c1", ["navigation"])
        info = CardSchedulingInfo(user_id="test-user", card_id="c1")
        sched_repo = FailingReviewLogRepository([info])

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=sched_repo,
            scheduling_service=SchedulingService(),
        )

        with pytest.raises(RuntimeError, match="review log failure"):
            await service.review_card("test-user", "c1", Rating.GOOD)

    @pytest.mark.asyncio
    async def test_isolates_scheduling_by_user(self):
        card = _make_card("c1", ["navigation"])
        user1_info = CardSchedulingInfo(
            user_id="user-1",
            card_id="c1",
            due=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        user2_info = CardSchedulingInfo(
            user_id="user-2",
            card_id="c1",
            due=datetime.now(timezone.utc) + timedelta(days=7),
        )

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([user1_info, user2_info]),
            scheduling_service=SchedulingService(),
        )

        user1_due = await service.get_due_cards(user_id="user-1")
        user2_due = await service.get_due_cards(user_id="user-2")

        assert [sc.card.card_id for sc in user1_due] == ["c1"]
        assert user2_due == []


class TestPracticeCards:
    @pytest.mark.asyncio
    async def test_returns_future_scheduled_cards_when_no_due_cards_exist(self):
        card = _make_card("c1", ["navigation"])
        future_info = _make_future_info("c1")

        service = StudyService(
            card_repo=FakeCardRepository([card]),
            scheduling_repo=FakeSchedulingRepository([future_info]),
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=5,
        )

        result = await service.get_practice_cards(user_id="test-user")

        assert [sc.card.card_id for sc in result] == ["c1"]

    @pytest.mark.asyncio
    async def test_practice_queue_keeps_due_cards_first_then_future_cards(self):
        due_card = _make_card("due", ["navigation"])
        future_card = _make_card("future", ["navigation"])
        due_info = _make_due_info("due")
        future_info = _make_future_info("future")

        service = StudyService(
            card_repo=FakeCardRepository([due_card, future_card]),
            scheduling_repo=FakeSchedulingRepository([future_info, due_info]),
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=5,
        )

        result = await service.get_practice_cards(user_id="test-user")

        assert [sc.card.card_id for sc in result] == ["due", "future"]

    @pytest.mark.asyncio
    async def test_practice_queue_respects_topic_filter(self):
        nav = _make_card("nav", ["navigation"])
        weather = _make_card("wx", ["wetterkunde"])
        infos = [_make_future_info("nav"), _make_future_info("wx")]

        service = StudyService(
            card_repo=FakeCardRepository([nav, weather]),
            scheduling_repo=FakeSchedulingRepository(infos),
            scheduling_service=SchedulingService(),
            new_card_limit_per_queue=5,
        )

        result = await service.get_practice_cards(
            user_id="test-user",
            topic=SksTopic.NAVIGATION,
        )

        assert [sc.card.card_id for sc in result] == ["nav"]
