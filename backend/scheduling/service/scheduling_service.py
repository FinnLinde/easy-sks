"""Application service that wraps the fsrs Scheduler.

All interactions with the fsrs library are confined to this service
and the mapper -- the rest of the application works exclusively
with our own domain objects.
"""

from __future__ import annotations

from fsrs import FSRS

from scheduling.mapper.fsrs_mapper import FsrsMapper
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog


class SchedulingService:
    """Provides spaced-repetition scheduling using the FSRS algorithm."""

    def __init__(self, fsrs: FSRS | None = None) -> None:
        self._fsrs = fsrs or FSRS()

    def review_card(
        self,
        card_info: CardSchedulingInfo,
        rating: Rating,
    ) -> tuple[CardSchedulingInfo, ReviewLog]:
        """Review a card and return its updated scheduling info and review log."""
        fsrs_card = FsrsMapper.to_fsrs_card(card_info)
        fsrs_rating = FsrsMapper.to_fsrs_rating(rating)

        updated_fsrs_card, fsrs_review_log = self._fsrs.review_card(
            fsrs_card, fsrs_rating
        )

        updated_info = FsrsMapper.to_card_scheduling_info(
            updated_fsrs_card,
            card_id=card_info.card_id,
            user_id=card_info.user_id,
        )
        review_log = FsrsMapper.to_review_log(
            fsrs_review_log,
            card_id=card_info.card_id,
            user_id=card_info.user_id,
        )

        return updated_info, review_log

    def get_retrievability(self, card_info: CardSchedulingInfo) -> float:
        """Return the current probability of correctly recalling the card."""
        fsrs_card = FsrsMapper.to_fsrs_card(card_info)
        return fsrs_card.get_retrievability()
