from __future__ import annotations

from datetime import datetime
from typing import Protocol

from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.review_log import ReviewLog


class SchedulingRepositoryPort(Protocol):
    """Port for retrieving and persisting card scheduling state."""

    async def list_for_user(self, user_id: str) -> list[CardSchedulingInfo]:
        """Return all scheduling info rows for a user."""
        ...

    async def get_by_user_and_card_id(
        self, user_id: str, card_id: str
    ) -> CardSchedulingInfo | None:
        """Return scheduling info for a given user/card pair, or None if not found."""
        ...

    async def get_due_for_user(
        self, user_id: str, before: datetime
    ) -> list[CardSchedulingInfo]:
        """Return due scheduling entries for a user before the given time."""
        ...

    async def save(self, info: CardSchedulingInfo) -> None:
        """Persist the given scheduling info."""
        ...

    async def save_review_log(self, log: ReviewLog) -> None:
        """Persist a review log entry for a completed review."""
        ...

    async def list_review_logs_for_user(self, user_id: str) -> list[ReviewLog]:
        """Return all review logs for a user."""
        ...
