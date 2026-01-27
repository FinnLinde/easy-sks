from __future__ import annotations

from app.fsrs.db import FsrsScheduler, SqlAlchemyUnitOfWork, get_session_factory

_session_factory = get_session_factory()


def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(_session_factory)


def get_scheduler() -> FsrsScheduler:
    return FsrsScheduler()
