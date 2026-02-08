"""FastAPI dependency injection wiring.

Provides async session, repository, and service instances via Depends().
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from card.db.card_repository import CardRepository
from database import async_session_factory
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.service.scheduling_service import SchedulingService
from study.service.study_service import StudyService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session that is committed/rolled-back automatically."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_study_service(
    session: AsyncSession = None,  # type: ignore[assignment]
) -> StudyService:
    """Build a StudyService wired to real repository adapters."""
    # When used via Depends(), FastAPI resolves get_db_session first.
    # We accept session as a parameter here so it can be injected.
    return StudyService(
        card_repo=CardRepository(session),
        scheduling_repo=SchedulingRepository(session),
        scheduling_service=SchedulingService(),
    )


async def get_card_repository(
    session: AsyncSession = None,  # type: ignore[assignment]
) -> CardRepository:
    """Build a CardRepository wired to a real DB session."""
    return CardRepository(session)
