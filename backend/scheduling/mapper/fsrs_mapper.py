"""Bidirectional mapping between our domain objects and the fsrs library objects."""

from fsrs import Card as FsrsCard
from fsrs import Rating as FsrsRating
from fsrs import ReviewLog as FsrsReviewLog
from fsrs import State as FsrsState

from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog

_CARD_STATE_TO_FSRS: dict[CardState, FsrsState] = {
    CardState.NEW: FsrsState.New,
    CardState.LEARNING: FsrsState.Learning,
    CardState.REVIEW: FsrsState.Review,
    CardState.RELEARNING: FsrsState.Relearning,
}

_FSRS_STATE_TO_CARD_STATE: dict[FsrsState, CardState] = {
    v: k for k, v in _CARD_STATE_TO_FSRS.items()
}

_RATING_TO_FSRS: dict[Rating, FsrsRating] = {
    Rating.AGAIN: FsrsRating.Again,
    Rating.HARD: FsrsRating.Hard,
    Rating.GOOD: FsrsRating.Good,
    Rating.EASY: FsrsRating.Easy,
}

_FSRS_RATING_TO_RATING: dict[FsrsRating, Rating] = {
    v: k for k, v in _RATING_TO_FSRS.items()
}


class FsrsMapper:
    """Stateless mapper between domain objects and fsrs library objects."""

    @staticmethod
    def to_fsrs_card(info: CardSchedulingInfo) -> FsrsCard:
        """Convert a CardSchedulingInfo to an fsrs Card."""
        return FsrsCard(
            due=info.due,
            stability=info.stability,
            difficulty=info.difficulty,
            elapsed_days=info.elapsed_days,
            scheduled_days=info.scheduled_days,
            reps=info.reps,
            lapses=info.lapses,
            state=_CARD_STATE_TO_FSRS[info.state],
            last_review=info.last_review,
        )

    @staticmethod
    def to_card_scheduling_info(
        fsrs_card: FsrsCard,
        card_id: str,
        user_id: str = "",
    ) -> CardSchedulingInfo:
        """Convert an fsrs Card back to a CardSchedulingInfo.

        The original card_id must be provided because the fsrs Card
        does not carry our domain identifier.
        """
        return CardSchedulingInfo(
            user_id=user_id,
            card_id=card_id,
            state=_FSRS_STATE_TO_CARD_STATE[fsrs_card.state],
            stability=fsrs_card.stability,
            difficulty=fsrs_card.difficulty,
            elapsed_days=fsrs_card.elapsed_days,
            scheduled_days=fsrs_card.scheduled_days,
            reps=fsrs_card.reps,
            lapses=fsrs_card.lapses,
            due=fsrs_card.due,
            last_review=getattr(fsrs_card, "last_review", None),
        )

    @staticmethod
    def to_fsrs_rating(rating: Rating) -> FsrsRating:
        """Convert a domain Rating to an fsrs Rating."""
        return _RATING_TO_FSRS[rating]

    @staticmethod
    def to_rating(fsrs_rating: FsrsRating) -> Rating:
        """Convert an fsrs Rating to a domain Rating."""
        return _FSRS_RATING_TO_RATING[fsrs_rating]

    @staticmethod
    def to_review_log(
        fsrs_log: FsrsReviewLog, card_id: str, user_id: str = ""
    ) -> ReviewLog:
        """Convert an fsrs ReviewLog to a domain ReviewLog.

        The original card_id must be provided because the fsrs ReviewLog
        does not carry our domain identifier.
        """
        return ReviewLog(
            user_id=user_id,
            card_id=card_id,
            rating=_FSRS_RATING_TO_RATING[fsrs_log.rating],
            reviewed_at=fsrs_log.review,
        )
