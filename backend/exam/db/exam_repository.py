"""Async PostgreSQL implementation of exam persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exam.db.exam_db_mapper import ExamDbMapper
from exam.db.exam_tables import ExamAnswerRow, ExamSessionRow
from exam.model.exam_answer import ExamAnswer
from exam.model.exam_session import ExamSession, ExamSessionStatus


class ExamRepository:
    """Repository adapter for exam sessions and answers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_session(self, session: ExamSession, answers: list[ExamAnswer]) -> None:
        self._session.add(ExamDbMapper.session_to_row(session))
        await self._session.flush()
        for answer in answers:
            self._session.add(ExamDbMapper.answer_to_row(answer))

    async def get_session(self, user_id: str, session_id: str) -> ExamSession | None:
        stmt = select(ExamSessionRow).where(
            ExamSessionRow.id == session_id,
            ExamSessionRow.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ExamDbMapper.session_to_domain(row)

    async def save_session(self, session: ExamSession) -> None:
        await self._session.merge(ExamDbMapper.session_to_row(session))

    async def list_answers(self, session_id: str) -> list[ExamAnswer]:
        stmt = (
            select(ExamAnswerRow)
            .where(ExamAnswerRow.session_id == session_id)
            .order_by(ExamAnswerRow.question_number.asc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [ExamDbMapper.answer_to_domain(row) for row in rows]

    async def get_answer(
        self,
        user_id: str,
        session_id: str,
        card_id: str,
    ) -> ExamAnswer | None:
        stmt = (
            select(ExamAnswerRow)
            .join(ExamSessionRow, ExamSessionRow.id == ExamAnswerRow.session_id)
            .where(
                ExamAnswerRow.session_id == session_id,
                ExamAnswerRow.card_id == card_id,
                ExamSessionRow.user_id == user_id,
            )
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ExamDbMapper.answer_to_domain(row)

    async def save_answer(self, answer: ExamAnswer) -> None:
        await self._session.merge(ExamDbMapper.answer_to_row(answer))

    async def list_completed_sessions_for_user(self, user_id: str) -> list[ExamSession]:
        stmt = (
            select(ExamSessionRow)
            .where(
                ExamSessionRow.user_id == user_id,
                ExamSessionRow.status != ExamSessionStatus.IN_PROGRESS.value,
            )
            .order_by(ExamSessionRow.started_at.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [ExamDbMapper.session_to_domain(row) for row in rows]
