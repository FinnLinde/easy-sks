"""Async PostgreSQL implementation of navigation persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from navigation.db.navigation_db_mapper import NavigationDbMapper
from navigation.db.navigation_tables import NavigationAnswerRow, NavigationSessionRow, NavigationTaskRow
from navigation.model.navigation_answer import NavigationAnswer
from navigation.model.navigation_session import NavigationSession, NavigationSessionStatus
from navigation.model.navigation_task import NavigationTask


class NavigationRepository:
    """Repository adapter for navigation tasks, sessions, and answers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_tasks_for_sheet(self, sheet_number: int) -> list[NavigationTask]:
        stmt = (
            select(NavigationTaskRow)
            .where(NavigationTaskRow.sheet_number == sheet_number)
            .order_by(NavigationTaskRow.task_number.asc())
        )
        result = await self._session.execute(stmt)
        return [NavigationDbMapper.task_to_domain(row) for row in result.scalars().all()]

    async def get_task(self, task_id: str) -> NavigationTask | None:
        row = await self._session.get(NavigationTaskRow, task_id)
        if row is None:
            return None
        return NavigationDbMapper.task_to_domain(row)

    async def get_distinct_sheet_numbers(self) -> list[int]:
        stmt = (
            select(NavigationTaskRow.sheet_number)
            .distinct()
            .order_by(NavigationTaskRow.sheet_number.asc())
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def count_tasks_per_sheet(self) -> dict[int, int]:
        from sqlalchemy import func

        stmt = (
            select(NavigationTaskRow.sheet_number, func.count(NavigationTaskRow.task_id))
            .group_by(NavigationTaskRow.sheet_number)
            .order_by(NavigationTaskRow.sheet_number.asc())
        )
        result = await self._session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def create_session(
        self, session: NavigationSession, answers: list[NavigationAnswer]
    ) -> None:
        self._session.add(NavigationDbMapper.session_to_row(session))
        await self._session.flush()
        for answer in answers:
            self._session.add(NavigationDbMapper.answer_to_row(answer))

    async def get_session(self, user_id: str, session_id: str) -> NavigationSession | None:
        stmt = select(NavigationSessionRow).where(
            NavigationSessionRow.id == session_id,
            NavigationSessionRow.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return NavigationDbMapper.session_to_domain(row)

    async def save_session(self, session: NavigationSession) -> None:
        await self._session.merge(NavigationDbMapper.session_to_row(session))

    async def list_answers(self, session_id: str) -> list[NavigationAnswer]:
        stmt = (
            select(NavigationAnswerRow)
            .where(NavigationAnswerRow.session_id == session_id)
            .order_by(NavigationAnswerRow.task_number.asc())
        )
        result = await self._session.execute(stmt)
        return [NavigationDbMapper.answer_to_domain(row) for row in result.scalars().all()]

    async def get_answer(
        self, user_id: str, session_id: str, task_id: str
    ) -> NavigationAnswer | None:
        stmt = (
            select(NavigationAnswerRow)
            .join(NavigationSessionRow, NavigationSessionRow.id == NavigationAnswerRow.session_id)
            .where(
                NavigationAnswerRow.session_id == session_id,
                NavigationAnswerRow.task_id == task_id,
                NavigationSessionRow.user_id == user_id,
            )
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return NavigationDbMapper.answer_to_domain(row)

    async def save_answer(self, answer: NavigationAnswer) -> None:
        await self._session.merge(NavigationDbMapper.answer_to_row(answer))

    async def list_completed_sessions_for_user(
        self, user_id: str
    ) -> list[NavigationSession]:
        stmt = (
            select(NavigationSessionRow)
            .where(
                NavigationSessionRow.user_id == user_id,
                NavigationSessionRow.status != NavigationSessionStatus.IN_PROGRESS.value,
            )
            .order_by(NavigationSessionRow.started_at.desc())
        )
        result = await self._session.execute(stmt)
        return [NavigationDbMapper.session_to_domain(row) for row in result.scalars().all()]
