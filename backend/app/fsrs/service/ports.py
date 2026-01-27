from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.fsrs.domain.models import CardLearningProgress, CardReviewEvent
from app.fsrs.domain.enums import ReviewRating


class ProgressRepository(Protocol):
    def get(self, user_id: UUID, card_id: UUID) -> CardLearningProgress | None:
        ...

    def upsert(self, progress: CardLearningProgress) -> None:
        ...

    def list_due(
        self,
        user_id: UUID,
        now: datetime,
        limit: int,
        deck_id: UUID | None = None,
    ) -> list[CardLearningProgress]:
        ...


class ReviewEventRepository(Protocol):
    def append(self, event: CardReviewEvent) -> None:
        ...

    def list_by_card(
        self,
        user_id: UUID,
        card_id: UUID,
        limit: int,
    ) -> list[CardReviewEvent]:
        ...


class Scheduler(Protocol):
    def schedule(
        self,
        progress: CardLearningProgress,
        rating: ReviewRating,
        reviewed_at: datetime,
    ) -> CardLearningProgress:
        ...


class UnitOfWork(AbstractContextManager, Protocol):
    progress_repo: ProgressRepository
    review_event_repo: ReviewEventRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
