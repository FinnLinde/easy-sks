from __future__ import annotations

from typing import Protocol

from card.model.card import Card


class ExamCardRepositoryPort(Protocol):
    """Port for exam-specific card lookup operations."""

    async def list_all(self) -> list[Card]:
        ...

    async def get_by_id(self, card_id: str) -> Card | None:
        ...
