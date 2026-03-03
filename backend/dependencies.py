"""FastAPI dependency injection wiring.

Provides async session, repository, and service instances via Depends().
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache
import os

from sqlalchemy.ext.asyncio import AsyncSession

from auth.model.authenticated_user import AuthenticatedUser
from card.db.card_repository import CardRepository
from database import async_session_factory
from exam.db.exam_repository import ExamRepository
from exam.service.exam_ai_config import ExamAiConfig
from exam.service.exam_service import ExamService
from exam.service.heuristic_exam_evaluator import HeuristicExamEvaluator
from exam.service.openai_exam_evaluator import OpenAiExamEvaluator
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.service.scheduling_service import SchedulingService
from study.service.exam_evaluator_adapter import ExamBackedStudyAnswerEvaluator
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
        answer_evaluator=ExamBackedStudyAnswerEvaluator(_build_exam_evaluator()),
    )


@lru_cache
def _build_exam_evaluator():
    config = ExamAiConfig()
    api_key = config.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return HeuristicExamEvaluator()
    return OpenAiExamEvaluator(
        api_key=api_key,
        model=config.openai_model,
        timeout_seconds=config.openai_timeout_seconds,
    )


async def get_exam_service(
    session: AsyncSession = None,  # type: ignore[assignment]
) -> ExamService:
    """Build an ExamService wired to real repository and evaluator adapters."""
    return ExamService(
        exam_repo=ExamRepository(session),
        card_repo=CardRepository(session),
        evaluator=_build_exam_evaluator(),
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
