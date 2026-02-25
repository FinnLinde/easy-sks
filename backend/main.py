"""Main entry point for the FastAPI application."""

from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from auth.service.auth_dependencies import get_current_user
from card.controller.card_controller import (
    get_card_repository as _card_repo_placeholder,
    router as card_router,
)
from dependencies import (
    get_card_repository,
    get_current_app_user,
    get_db_session,
    get_study_service,
)
from study.controller.study_controller import (
    get_current_app_user as _app_user_placeholder,
    get_study_service as _study_svc_placeholder,
    router as study_router,
)

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
    allow_origins=["http://localhost:3000"],
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


app.dependency_overrides[_study_svc_placeholder] = _wired_study_service
app.dependency_overrides[_card_repo_placeholder] = _wired_card_repository
app.dependency_overrides[_app_user_placeholder] = _wired_current_app_user

# -- Routers ---------------------------------------------------------------

# Authenticated router: every route mounted here requires a valid token.
authenticated_router = APIRouter(dependencies=[Depends(get_current_user)])
authenticated_router.include_router(study_router)
authenticated_router.include_router(card_router)

app.include_router(authenticated_router)

# Public router: no authentication required.
public_router = APIRouter(tags=["General"])


@public_router.get("/")
async def root():
    return {"message": "Welcome to Easy SKS API"}


@public_router.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(public_router)
