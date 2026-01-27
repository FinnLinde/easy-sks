from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.fsrs.domain.defaults import default_progress
from app.fsrs.domain.enums import ReviewRating
from app.fsrs.domain.models import CardLearningProgress, CardReviewEvent

from .ports import Scheduler, UnitOfWork


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_due_queue(
    uow: UnitOfWork,
    user_id: UUID,
    now: datetime,
    limit: int,
    deck_id: UUID | None = None,
) -> list[CardLearningProgress]:
    now = _ensure_utc(now)
    with uow:
        return uow.progress_repo.list_due(user_id, now, limit, deck_id=deck_id)


def ensure_progress(
    uow: UnitOfWork,
    user_id: UUID,
    card_id: UUID,
    now: datetime | None = None,
) -> CardLearningProgress:
    timestamp = _ensure_utc(now) if now is not None else _utc_now()
    with uow:
        progress = uow.progress_repo.get(user_id, card_id)
        if progress is not None:
            return progress

        progress = default_progress(user_id, card_id, timestamp)
        uow.progress_repo.upsert(progress)
        uow.commit()
        return progress


def grade_card(
    uow: UnitOfWork,
    scheduler: Scheduler,
    user_id: UUID,
    card_id: UUID,
    rating: ReviewRating,
    reviewed_at: datetime | None = None,
) -> CardLearningProgress:
    timestamp = _ensure_utc(reviewed_at) if reviewed_at is not None else _utc_now()
    with uow:
        progress = uow.progress_repo.get(user_id, card_id)
        if progress is None:
            progress = default_progress(user_id, card_id, timestamp)

        updated = scheduler.schedule(progress, rating, timestamp)
        event = CardReviewEvent(
            user_id=user_id,
            card_id=card_id,
            reviewed_at=timestamp,
            rating=rating,
        )

        uow.progress_repo.upsert(updated)
        uow.review_event_repo.append(event)
        uow.commit()
        return updated
