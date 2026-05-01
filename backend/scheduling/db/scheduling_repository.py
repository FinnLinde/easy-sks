"""Async PostgreSQL implementation of SchedulingRepositoryPort."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduling.db.scheduling_db_mapper import SchedulingDbMapper
from scheduling.db.review_log_table import ReviewLogRow
from scheduling.db.scheduling_table import CardSchedulingInfoRow
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.review_log import ReviewLog


class SchedulingRepository:
    """Implements SchedulingRepositoryPort using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[CardSchedulingInfo]:
        stmt = select(CardSchedulingInfoRow)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [SchedulingDbMapper.info_to_domain(row) for row in rows]

    async def get_by_card_id(self, card_id: str) -> CardSchedulingInfo | None:
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.card_id == card_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return SchedulingDbMapper.info_to_domain(row)

    async def get_due(self, before: datetime) -> list[CardSchedulingInfo]:
        """Return due rows in a deterministic queue order (due ASC, last_review ASC NULLS FIRST, card_id ASC)."""
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.due <= before
        ).order_by(
            CardSchedulingInfoRow.due.asc(),
            CardSchedulingInfoRow.last_review.asc().nullsfirst(),
            CardSchedulingInfoRow.card_id.asc(),
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [SchedulingDbMapper.info_to_domain(row) for row in rows]

    async def save(self, info: CardSchedulingInfo) -> None:
        row = SchedulingDbMapper.info_to_row(info)
        await self._session.merge(row)

    async def save_review_log(self, log: ReviewLog) -> None:
        row = SchedulingDbMapper.log_to_row(log)
        self._session.add(row)

    async def list_review_logs(self) -> list[ReviewLog]:
        stmt = select(ReviewLogRow).order_by(ReviewLogRow.reviewed_at.desc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [SchedulingDbMapper.log_to_domain(row) for row in rows]
