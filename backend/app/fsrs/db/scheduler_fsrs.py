from __future__ import annotations

from datetime import datetime, timezone

from fsrs.card import Card as FsrsCard
from fsrs.rating import Rating as FsrsRating
from fsrs.scheduler import Scheduler as FsrsEngine
from fsrs.state import State as FsrsState

from app.fsrs.domain.defaults import DEFAULT_PARAMETERS, DEFAULT_TARGET_RETENTION
from app.fsrs.domain.enums import CardState, ReviewRating
from app.fsrs.domain.models import CardLearningProgress
from app.fsrs.service.ports import Scheduler


class FsrsScheduler(Scheduler):
    def __init__(
        self,
        parameters: tuple[float, ...] = DEFAULT_PARAMETERS,
        desired_retention: float = DEFAULT_TARGET_RETENTION,
    ) -> None:
        self._scheduler = FsrsEngine(
            parameters=parameters,
            desired_retention=desired_retention,
        )

    def schedule(
        self,
        progress: CardLearningProgress,
        rating: ReviewRating,
        reviewed_at: datetime,
    ) -> CardLearningProgress:
        if progress.state == CardState.SUSPENDED:
            return progress

        reviewed_at = self._ensure_utc(reviewed_at)
        fsrs_rating = self._to_fsrs_rating(rating)
        fsrs_state, step = self._to_fsrs_state(progress.state)

        card = FsrsCard(
            card_id=progress.card_id.int,
            state=fsrs_state,
            step=step,
            stability=progress.stability,
            difficulty=progress.difficulty,
            due=progress.due_at,
            last_review=progress.last_reviewed_at,
        )

        updated_card, _ = self._scheduler.review_card(
            card=card,
            rating=fsrs_rating,
            review_datetime=reviewed_at,
        )

        return CardLearningProgress(
            user_id=progress.user_id,
            card_id=progress.card_id,
            stability=updated_card.stability or progress.stability,
            difficulty=updated_card.difficulty or progress.difficulty,
            due_at=updated_card.due,
            last_reviewed_at=updated_card.last_review,
            state=self._from_fsrs_state(updated_card.state),
        )

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _to_fsrs_rating(rating: ReviewRating) -> FsrsRating:
        return {
            ReviewRating.AGAIN: FsrsRating.Again,
            ReviewRating.HARD: FsrsRating.Hard,
            ReviewRating.GOOD: FsrsRating.Good,
            ReviewRating.EASY: FsrsRating.Easy,
        }[rating]

    @staticmethod
    def _to_fsrs_state(state: CardState) -> tuple[FsrsState, int | None]:
        if state == CardState.NEW:
            return FsrsState.Learning, 0
        return FsrsState.Review, None

    @staticmethod
    def _from_fsrs_state(state: FsrsState) -> CardState:
        if state == FsrsState.Review:
            return CardState.REVIEW
        return CardState.NEW
