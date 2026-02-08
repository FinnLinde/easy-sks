from __future__ import annotations

from typing import Protocol

from card.model.card import Card


class CardRepositoryPort(Protocol):
    """Port for retrieving cards from persistence."""

    def get_by_id(self, card_id: str) -> Card | None:
        """Return the card with the given ID, or None if not found."""
        ...

    def get_by_tags(self, tags: list[str]) -> list[Card]:
        """Return all cards that have at least one of the given tags."""
        ...
