from __future__ import annotations

from datetime import datetime
from typing import Protocol

from scheduling.model.card_scheduling_info import CardSchedulingInfo


class SchedulingRepositoryPort(Protocol):
    """Port for retrieving and persisting card scheduling state."""

    def get_by_card_id(self, card_id: str) -> CardSchedulingInfo | None:
        """Return the scheduling info for the given card, or None if not found."""
        ...

    def get_due(self, before: datetime) -> list[CardSchedulingInfo]:
        """Return all scheduling entries that are due before the given time."""
        ...

    def save(self, info: CardSchedulingInfo) -> None:
        """Persist the given scheduling info."""
        ...
