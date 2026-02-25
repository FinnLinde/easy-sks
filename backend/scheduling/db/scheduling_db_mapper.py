"""Maps between scheduling domain objects and ORM rows."""

from __future__ import annotations

from scheduling.db.review_log_table import ReviewLogRow
from scheduling.db.scheduling_table import CardSchedulingInfoRow
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog


class SchedulingDbMapper:
    """Stateless mapper between scheduling domain objects and database rows."""

    @staticmethod
    def info_to_domain(row: CardSchedulingInfoRow) -> CardSchedulingInfo:
        """Convert a CardSchedulingInfoRow to a domain object."""
        return CardSchedulingInfo(
            user_id=row.user_id,
            card_id=row.card_id,
            state=CardState(row.state),
            stability=row.stability,
            difficulty=row.difficulty,
            elapsed_days=row.elapsed_days,
            scheduled_days=row.scheduled_days,
            reps=row.reps,
            lapses=row.lapses,
            due=row.due,
            last_review=row.last_review,
        )

    @staticmethod
    def info_to_row(info: CardSchedulingInfo) -> CardSchedulingInfoRow:
        """Convert a domain CardSchedulingInfo to an ORM row."""
        return CardSchedulingInfoRow(
            user_id=info.user_id,
            card_id=info.card_id,
            state=int(info.state),
            stability=info.stability,
            difficulty=info.difficulty,
            elapsed_days=info.elapsed_days,
            scheduled_days=info.scheduled_days,
            reps=info.reps,
            lapses=info.lapses,
            due=info.due,
            last_review=info.last_review,
        )

    @staticmethod
    def log_to_domain(row: ReviewLogRow) -> ReviewLog:
        """Convert a ReviewLogRow to a domain ReviewLog."""
        return ReviewLog(
            card_id=row.card_id,
            rating=Rating(row.rating),
            reviewed_at=row.reviewed_at,
            user_id=row.user_id,
            review_duration_ms=row.review_duration_ms,
        )

    @staticmethod
    def log_to_row(log: ReviewLog) -> ReviewLogRow:
        """Convert a domain ReviewLog to an ORM row."""
        return ReviewLogRow(
            user_id=log.user_id,
            card_id=log.card_id,
            rating=int(log.rating),
            reviewed_at=log.reviewed_at,
            review_duration_ms=log.review_duration_ms,
        )
