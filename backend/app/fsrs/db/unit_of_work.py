from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.fsrs.service.ports import UnitOfWork

from .repositories import SqlAlchemyProgressRepository, SqlAlchemyReviewEventRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.progress_repo: SqlAlchemyProgressRepository
        self.review_event_repo: SqlAlchemyReviewEventRepository

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.progress_repo = SqlAlchemyProgressRepository(self._session)
        self.review_event_repo = SqlAlchemyReviewEventRepository(self._session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._session is None:
            return
        if exc_type is not None:
            self._session.rollback()
        self._session.close()

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork has no active session.")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("UnitOfWork has no active session.")
        self._session.rollback()
