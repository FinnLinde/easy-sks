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

from auth.service.auth_dependencies import get_current_user
from billing.controller.billing_controller import (
    get_billing_service as _billing_svc_placeholder,
    get_current_app_user as _billing_app_user_placeholder,
    router as billing_router,
)
from card.controller.card_controller import (
    get_card_repository as _card_repo_placeholder,
    router as card_router,
)
from dependencies import (
    get_billing_service,
    get_card_repository,
    get_current_app_user,
    get_db_session,
    get_exam_service,
    get_navigation_service,
    get_study_service,
    get_user_profile_service,
)
from exam.controller.exam_controller import (
    get_current_app_user as _exam_app_user_placeholder,
    get_exam_service as _exam_svc_placeholder,
    router as exam_router,
)
from navigation.controller.navigation_controller import (
    get_current_app_user as _nav_app_user_placeholder,
    get_navigation_service as _nav_svc_placeholder,
    router as navigation_router,
)
from study.controller.study_controller import (
    get_current_app_user as _app_user_placeholder,
    get_study_service as _study_svc_placeholder,
    router as study_router,
)
from user.controller.user_controller import (
    get_billing_service as _user_billing_service_placeholder,
    get_current_app_user as _user_app_user_placeholder,
    get_user_profile_service as _user_profile_service_placeholder,
    router as user_router,
)


def _get_cors_origins() -> list[str]:
    raw_origins = os.getenv("APP_CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:3000"]

app = FastAPI(
    title="Easy SKS API",
    version="1.0.0",
    description="API for Easy SKS flashcard study application",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# -- CORS ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Dependency overrides --------------------------------------------------
# The controllers declare lightweight placeholder dependencies; we override
# them here with the real wired-up implementations.


async def _wired_study_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_study_service(session)


async def _wired_card_repository(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_card_repository(session)


async def _wired_current_app_user(
    session: AsyncSession = Depends(get_db_session),
    auth_user=Depends(get_current_user),
):
    return await get_current_app_user(auth_user=auth_user, session=session)


async def _wired_user_profile_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_user_profile_service(session)


async def _wired_exam_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_exam_service(session)


async def _wired_navigation_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_navigation_service(session)


async def _wired_billing_service(
    session: AsyncSession = Depends(get_db_session),
):
    return await get_billing_service(session)


app.dependency_overrides[_study_svc_placeholder] = _wired_study_service
app.dependency_overrides[_card_repo_placeholder] = _wired_card_repository
app.dependency_overrides[_app_user_placeholder] = _wired_current_app_user
app.dependency_overrides[_exam_svc_placeholder] = _wired_exam_service
app.dependency_overrides[_exam_app_user_placeholder] = _wired_current_app_user
app.dependency_overrides[_user_app_user_placeholder] = _wired_current_app_user
app.dependency_overrides[_user_profile_service_placeholder] = (
    _wired_user_profile_service
)
app.dependency_overrides[_user_billing_service_placeholder] = _wired_billing_service
app.dependency_overrides[_billing_svc_placeholder] = _wired_billing_service
app.dependency_overrides[_billing_app_user_placeholder] = _wired_current_app_user
app.dependency_overrides[_nav_svc_placeholder] = _wired_navigation_service
app.dependency_overrides[_nav_app_user_placeholder] = _wired_current_app_user

# -- Routers ---------------------------------------------------------------

# Authenticated router: every route mounted here requires a valid token.
authenticated_router = APIRouter(dependencies=[Depends(get_current_user)])
authenticated_router.include_router(study_router)
authenticated_router.include_router(card_router)
authenticated_router.include_router(user_router)
authenticated_router.include_router(exam_router)
authenticated_router.include_router(navigation_router)

app.include_router(authenticated_router)
app.include_router(billing_router)

# Public router: no authentication required.
public_router = APIRouter(tags=["General"])


@public_router.get("/")
async def root():
    return {"message": "Welcome to Easy SKS API"}


@public_router.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(public_router)
