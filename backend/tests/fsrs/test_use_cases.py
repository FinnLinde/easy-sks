from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.fsrs.domain.defaults import (
    DEFAULT_INITIAL_DIFFICULTY,
    DEFAULT_INITIAL_STABILITY,
)
from app.fsrs.domain.enums import CardState, ReviewRating
from app.fsrs.domain.models import CardLearningProgress, CardReviewEvent
from app.fsrs.service.use_cases import ensure_progress, get_due_queue, grade_card


class FakeProgressRepository:
    def __init__(
        self,
        progress: CardLearningProgress | None = None,
        due_list: list[CardLearningProgress] | None = None,
    ) -> None:
        self._progress = progress
        self._due_list = due_list or []
        self.upserts: list[CardLearningProgress] = []
        self.list_due_calls: list[dict[str, object]] = []

    def get(self, user_id: UUID, card_id: UUID) -> CardLearningProgress | None:
        return self._progress

    def upsert(self, progress: CardLearningProgress) -> None:
        self.upserts.append(progress)
        self._progress = progress

    def list_due(
        self,
        user_id: UUID,
        now: datetime,
        limit: int,
        deck_id: UUID | None = None,
    ) -> list[CardLearningProgress]:
        self.list_due_calls.append(
            {
                "user_id": user_id,
                "now": now,
                "limit": limit,
                "deck_id": deck_id,
            }
        )
        return list(self._due_list)


class FakeReviewEventRepository:
    def __init__(self) -> None:
        self.events: list[CardReviewEvent] = []

    def append(self, event: CardReviewEvent) -> None:
        self.events.append(event)

    def list_by_card(
        self,
        user_id: UUID,
        card_id: UUID,
        limit: int,
    ) -> list[CardReviewEvent]:
        return list(self.events)[:limit]


@dataclass
class FakeUnitOfWork:
    progress_repo: FakeProgressRepository
    review_event_repo: FakeReviewEventRepository
    commits: int = 0
    rollbacks: int = 0

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class FakeScheduler:
    def __init__(self) -> None:
        self.calls: list[tuple[CardLearningProgress, ReviewRating, datetime]] = []

    def schedule(
        self,
        progress: CardLearningProgress,
        rating: ReviewRating,
        reviewed_at: datetime,
    ) -> CardLearningProgress:
        self.calls.append((progress, rating, reviewed_at))
        return CardLearningProgress(
            user_id=progress.user_id,
            card_id=progress.card_id,
            stability=progress.stability + 1.0,
            difficulty=progress.difficulty + 0.5,
            due_at=reviewed_at + timedelta(days=1),
            last_reviewed_at=reviewed_at,
            state=CardState.REVIEW,
        )


def _progress(user_id: UUID, card_id: UUID, due_at: datetime) -> CardLearningProgress:
    return CardLearningProgress(
        user_id=user_id,
        card_id=card_id,
        stability=DEFAULT_INITIAL_STABILITY,
        difficulty=DEFAULT_INITIAL_DIFFICULTY,
        due_at=due_at,
        last_reviewed_at=None,
        state=CardState.NEW,
    )


def test_get_due_queue_returns_due_items() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    due_at = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    progress = _progress(user_id, card_id, due_at)
    repo = FakeProgressRepository(due_list=[progress])
    uow = FakeUnitOfWork(repo, FakeReviewEventRepository())
    naive_now = datetime(2024, 1, 1, 11, 0)

    # // when
    result = get_due_queue(uow, user_id, naive_now, limit=5)

    # // then
    assert result == [progress]
    assert repo.list_due_calls[0]["limit"] == 5
    assert repo.list_due_calls[0]["now"].tzinfo == timezone.utc


def test_ensure_progress_returns_existing_progress() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    now = datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc)
    existing = _progress(user_id, card_id, now)
    repo = FakeProgressRepository(progress=existing)
    uow = FakeUnitOfWork(repo, FakeReviewEventRepository())

    # // when
    result = ensure_progress(uow, user_id, card_id, now=now)

    # // then
    assert result == existing
    assert repo.upserts == []
    assert uow.commits == 0


def test_ensure_progress_creates_default_when_missing() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    now = datetime(2024, 1, 3, 8, 0, tzinfo=timezone.utc)
    repo = FakeProgressRepository(progress=None)
    uow = FakeUnitOfWork(repo, FakeReviewEventRepository())

    # // when
    result = ensure_progress(uow, user_id, card_id, now=now)

    # // then
    assert result.user_id == user_id
    assert result.card_id == card_id
    assert result.due_at == now
    assert result.state == CardState.NEW
    assert result.stability == DEFAULT_INITIAL_STABILITY
    assert result.difficulty == DEFAULT_INITIAL_DIFFICULTY
    assert repo.upserts == [result]
    assert uow.commits == 1


def test_grade_card_appends_event_and_updates_progress() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    reviewed_at = datetime(2024, 1, 4, 7, 30, tzinfo=timezone.utc)
    repo = FakeProgressRepository(progress=None)
    events = FakeReviewEventRepository()
    uow = FakeUnitOfWork(repo, events)
    scheduler = FakeScheduler()

    # // when
    result = grade_card(
        uow=uow,
        scheduler=scheduler,
        user_id=user_id,
        card_id=card_id,
        rating=ReviewRating.GOOD,
        reviewed_at=reviewed_at,
    )

    # // then
    assert result.state == CardState.REVIEW
    assert result.last_reviewed_at == reviewed_at
    assert repo.upserts[-1] == result
    assert len(events.events) == 1
    assert events.events[0].rating == ReviewRating.GOOD
    assert events.events[0].reviewed_at == reviewed_at
    assert uow.commits == 1
    assert scheduler.calls[0][1] == ReviewRating.GOOD
