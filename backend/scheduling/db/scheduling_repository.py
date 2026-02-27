"""Async PostgreSQL implementation of SchedulingRepositoryPort."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduling.db.scheduling_db_mapper import SchedulingDbMapper
from scheduling.db.scheduling_table import CardSchedulingInfoRow
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.review_log import ReviewLog


class SchedulingRepository:
    """Implements SchedulingRepositoryPort using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: str) -> list[CardSchedulingInfo]:
        """Return all scheduling entries for the given user."""
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.user_id == user_id
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [SchedulingDbMapper.info_to_domain(row) for row in rows]

    async def get_by_user_and_card_id(
        self, user_id: str, card_id: str
    ) -> CardSchedulingInfo | None:
        """Return scheduling info for the given user/card pair, or None."""
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.user_id == user_id,
            CardSchedulingInfoRow.card_id == card_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return SchedulingDbMapper.info_to_domain(row)

    async def get_due_for_user(
        self, user_id: str, before: datetime
    ) -> list[CardSchedulingInfo]:
        """Return due rows with a deterministic queue order.

        Ordering is intentionally explicit so repeated calls produce the same
        study sequence for equal data:
        1) due ASC
        2) last_review ASC NULLS FIRST
        3) card_id ASC
        """
        stmt = select(CardSchedulingInfoRow).where(
            CardSchedulingInfoRow.user_id == user_id,
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
        """Insert or update a scheduling info record."""
        row = SchedulingDbMapper.info_to_row(info)
        await self._session.merge(row)

    async def save_review_log(self, log: ReviewLog) -> None:
        """Insert a review log entry."""
        row = SchedulingDbMapper.log_to_row(log)
        self._session.add(row)
