"""FastAPI dependency injection wiring.

Provides async session, repository, and service instances via Depends().
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from auth.model.authenticated_user import AuthenticatedUser
from card.db.card_repository import CardRepository
from database import async_session_factory
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.service.scheduling_service import SchedulingService
from study.service.study_service import StudyService
from user.db.user_repository import UserRepository
from user.model.app_user import AppUser
from user.service.user_profile_service import UserProfileService
from user.service.user_provisioning_service import UserProvisioningService


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


async def get_user_repository(
    session: AsyncSession = None,  # type: ignore[assignment]
) -> UserRepository:
    """Build a UserRepository wired to a real DB session."""
    return UserRepository(session)


async def get_user_profile_service(
    session: AsyncSession = None,  # type: ignore[assignment]
) -> UserProfileService:
    """Build a UserProfileService wired to a real DB session."""
    return UserProfileService(UserRepository(session))


async def get_current_app_user(
    auth_user: AuthenticatedUser,
    session: AsyncSession,
) -> AppUser:
    """Create/load the local app user for the authenticated principal."""
    provisioning = UserProvisioningService(UserRepository(session))
    return await provisioning.get_or_create_for_authenticated_user(auth_user)
