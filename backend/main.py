"""Main entry point for the FastAPI application."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR / ".env", override=False)
load_dotenv(_BACKEND_DIR / ".env.local", override=False)

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from card.controller.card_controller import (
    get_card_repository as _card_repo_placeholder,
    router as card_router,
)
from dependencies import (
    get_audio_transcription_service,
    get_card_repository,
    get_db_session,
    get_exam_service,
    get_navigation_service,
    get_settings_service,
    get_study_service,
)
from exam.controller.exam_controller import (
    get_exam_service as _exam_svc_placeholder,
    router as exam_router,
)
from navigation.controller.navigation_controller import (
    get_navigation_service as _nav_svc_placeholder,
    router as navigation_router,
)
from settings.controller.settings_controller import (
    get_settings_service as _settings_svc_placeholder,
    router as settings_router,
)
from study.controller.study_controller import (
    get_study_service as _study_svc_placeholder,
    router as study_router,
)
from transcription.controller.transcription_controller import (
    get_audio_transcription_service as _transcription_svc_placeholder,
    router as transcription_router,
)


def _get_cors_origins() -> list[str]:
    raw_origins = os.getenv("APP_CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:3000"]


app = FastAPI(
    title="Easy SKS API",
    version="1.0.0",
    description="Open-source flashcard study app for the Sportkuestenschifferschein (SKS)",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Dependency overrides --------------------------------------------------
# Controllers declare lightweight placeholder dependencies; we override them
# here with the real wired-up implementations.


async def _wired_study_service(session: AsyncSession = Depends(get_db_session)):
    return await get_study_service(session)


async def _wired_card_repository(session: AsyncSession = Depends(get_db_session)):
    return await get_card_repository(session)


async def _wired_exam_service(session: AsyncSession = Depends(get_db_session)):
    return await get_exam_service(session)


async def _wired_navigation_service(session: AsyncSession = Depends(get_db_session)):
    return await get_navigation_service(session)


async def _wired_audio_transcription_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_audio_transcription_service(session)


async def _wired_settings_service(session: AsyncSession = Depends(get_db_session)):
    return await get_settings_service(session)


app.dependency_overrides[_study_svc_placeholder] = _wired_study_service
app.dependency_overrides[_card_repo_placeholder] = _wired_card_repository
app.dependency_overrides[_exam_svc_placeholder] = _wired_exam_service
app.dependency_overrides[_nav_svc_placeholder] = _wired_navigation_service
app.dependency_overrides[_transcription_svc_placeholder] = (
    _wired_audio_transcription_service
)
app.dependency_overrides[_settings_svc_placeholder] = _wired_settings_service


# -- Routers ---------------------------------------------------------------

app.include_router(study_router)
app.include_router(card_router)
app.include_router(exam_router)
app.include_router(navigation_router)
app.include_router(transcription_router)
app.include_router(settings_router)


public_router = APIRouter(tags=["General"])


@public_router.get("/")
async def root():
    return {"message": "Welcome to Easy SKS API"}


@public_router.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(public_router)
