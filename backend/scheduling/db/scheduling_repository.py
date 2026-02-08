"""Async PostgreSQL implementation of SchedulingRepositoryPort."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduling.db.scheduling_db_mapper import SchedulingDbMapper
from scheduling.db.scheduling_table import CardSchedulingInfoRow
from scheduling.model.card_scheduling_info import CardSchedulingInfo


class SchedulingRepository:
    """Implements SchedulingRepositoryPort using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_card_id(self, card_id: str) -> CardSchedulingInfo | None:
        """Return the scheduling info for the given card, or None."""
        row = await self._session.get(CardSchedulingInfoRow, card_id)
        if row is None:
            return None
        return SchedulingDbMapper.info_to_domain(row)

    async def get_due(self, before: datetime) -> list[CardSchedulingInfo]:
        """Return all scheduling entries that are due before the given time."""
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.due <= before
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [SchedulingDbMapper.info_to_domain(row) for row in rows]

    async def save(self, info: CardSchedulingInfo) -> None:
        """Insert or update a scheduling info record."""
        row = SchedulingDbMapper.info_to_row(info)
        await self._session.merge(row)
