"""FastAPI dependency injection wiring.

Provides async session, repository, and service instances via Depends().
AI evaluators are built per request based on the current `app_settings` row,
so toggling AI in the settings page takes effect without restarting the server.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from card.db.card_repository import CardRepository
from database import async_session_factory
from exam.db.exam_repository import ExamRepository
from exam.service.exam_service import ExamService
from exam.service.heuristic_exam_evaluator import HeuristicExamEvaluator
from exam.service.openai_exam_evaluator import OpenAiExamEvaluator
from navigation.db.navigation_repository import NavigationRepository
from navigation.service.heuristic_navigation_evaluator import HeuristicNavigationEvaluator
from navigation.service.navigation_service import NavigationService
from navigation.service.openai_navigation_evaluator import OpenAiNavigationEvaluator
from scheduling.db.scheduling_repository import SchedulingRepository
from scheduling.service.scheduling_service import SchedulingService
from settings.db.settings_repository import SettingsRepository
from settings.model.app_settings import AppSettings
from settings.service.settings_service import SettingsService
from study.service.exam_evaluator_adapter import ExamBackedStudyAnswerEvaluator
from study.service.study_service import StudyService
from transcription.service.audio_transcription_service import AudioTranscriptionService
from transcription.service.openai_audio_transcriber import OpenAiAudioTranscriber

OPENAI_CHAT_TIMEOUT_SECONDS = 25.0
OPENAI_TRANSCRIPTION_TIMEOUT_SECONDS = 30.0
TRANSCRIPTION_DEFAULT_LANGUAGE = "de"
TRANSCRIPTION_MAX_FILE_BYTES = 10 * 1024 * 1024


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session that is committed/rolled-back automatically."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_settings_service(session: AsyncSession) -> SettingsService:
    return SettingsService(SettingsRepository(session))


async def _read_settings(session: AsyncSession) -> AppSettings:
    return await (await get_settings_service(session)).get()


def _build_exam_evaluator(settings: AppSettings):
    if not settings.ai_ready:
        return HeuristicExamEvaluator()
    return OpenAiExamEvaluator(
        api_key=settings.openai_api_key or "",
        model=settings.openai_chat_model,
        timeout_seconds=OPENAI_CHAT_TIMEOUT_SECONDS,
    )


def _build_navigation_evaluator(settings: AppSettings):
    if not settings.ai_ready:
        return HeuristicNavigationEvaluator()
    return OpenAiNavigationEvaluator(
        api_key=settings.openai_api_key or "",
        model=settings.openai_chat_model,
        timeout_seconds=OPENAI_CHAT_TIMEOUT_SECONDS,
    )


def _build_audio_transcription_service(settings: AppSettings) -> AudioTranscriptionService:
    transcriber = None
    if settings.ai_ready:
        transcriber = OpenAiAudioTranscriber(
            api_key=settings.openai_api_key or "",
            model=settings.openai_transcription_model,
            timeout_seconds=OPENAI_TRANSCRIPTION_TIMEOUT_SECONDS,
        )
    return AudioTranscriptionService(
        transcriber=transcriber,
        default_language=TRANSCRIPTION_DEFAULT_LANGUAGE,
        max_file_bytes=TRANSCRIPTION_MAX_FILE_BYTES,
    )


async def get_study_service(session: AsyncSession) -> StudyService:
    settings = await _read_settings(session)
    return StudyService(
        card_repo=CardRepository(session),
        scheduling_repo=SchedulingRepository(session),
        scheduling_service=SchedulingService(),
        answer_evaluator=ExamBackedStudyAnswerEvaluator(_build_exam_evaluator(settings)),
    )


async def get_exam_service(session: AsyncSession) -> ExamService:
    settings = await _read_settings(session)
    return ExamService(
        exam_repo=ExamRepository(session),
        card_repo=CardRepository(session),
        evaluator=_build_exam_evaluator(settings),
    )


async def get_navigation_service(session: AsyncSession) -> NavigationService:
    settings = await _read_settings(session)
    return NavigationService(
        repository=NavigationRepository(session),
        evaluator=_build_navigation_evaluator(settings),
    )


async def get_audio_transcription_service(
    session: AsyncSession,
) -> AudioTranscriptionService:
    settings = await _read_settings(session)
    return _build_audio_transcription_service(settings)


async def get_card_repository(session: AsyncSession) -> CardRepository:
    return CardRepository(session)
