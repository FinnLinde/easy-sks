from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.fsrs.db.scheduler_fsrs import FsrsScheduler
from app.fsrs.domain.defaults import (
    DEFAULT_INITIAL_DIFFICULTY,
    DEFAULT_INITIAL_STABILITY,
)
from app.fsrs.domain.enums import CardState, ReviewRating
from app.fsrs.domain.models import CardLearningProgress


def test_scheduler_returns_same_progress_when_suspended() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    reviewed_at = datetime(2024, 1, 5, 10, 0, tzinfo=timezone.utc)
    progress = CardLearningProgress(
        user_id=user_id,
        card_id=card_id,
        stability=DEFAULT_INITIAL_STABILITY,
        difficulty=DEFAULT_INITIAL_DIFFICULTY,
        due_at=reviewed_at,
        last_reviewed_at=None,
        state=CardState.SUSPENDED,
    )
    scheduler = FsrsScheduler()

    # // when
    result = scheduler.schedule(progress, ReviewRating.GOOD, reviewed_at)

    # // then
    assert result == progress


def test_scheduler_updates_due_date_for_active_progress() -> None:
    # // given
    user_id = uuid4()
    card_id = uuid4()
    reviewed_at = datetime(2024, 1, 6, 10, 0, tzinfo=timezone.utc)
    progress = CardLearningProgress(
        user_id=user_id,
        card_id=card_id,
        stability=DEFAULT_INITIAL_STABILITY,
        difficulty=DEFAULT_INITIAL_DIFFICULTY,
        due_at=reviewed_at,
        last_reviewed_at=None,
        state=CardState.NEW,
    )
    scheduler = FsrsScheduler()

    # // when
    result = scheduler.schedule(progress, ReviewRating.GOOD, reviewed_at)

    # // then
    assert result.last_reviewed_at == reviewed_at
    assert result.due_at >= reviewed_at
    assert result.state in {CardState.NEW, CardState.REVIEW}
