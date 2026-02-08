"""Async PostgreSQL implementation of CardRepositoryPort."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from card.db.card_db_mapper import CardDbMapper
from card.db.card_table import CardRow
from card.model.card import Card


class CardRepository:
    """Implements CardRepositoryPort using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, card_id: str) -> Card | None:
        """Return the card with the given ID, or None if not found."""
        row = await self._session.get(CardRow, card_id)
        if row is None:
            return None
        return CardDbMapper.to_domain(row)

    async def get_by_tags(self, tags: list[str]) -> list[Card]:
        """Return all cards that have at least one of the given tags."""
        stmt = select(CardRow).where(CardRow.tags.overlap(tags))
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [CardDbMapper.to_domain(row) for row in rows]

    async def save(self, card: Card) -> None:
        """Insert or update a card."""
        row = CardDbMapper.to_row(card)
        await self._session.merge(row)
