"""Main entry point for the FastAPI application."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from card.controller.card_controller import (
    get_card_repository as _card_repo_placeholder,
    router as card_router,
)
from dependencies import get_card_repository, get_db_session, get_study_service
from study.controller.study_controller import (
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


app.dependency_overrides[_study_svc_placeholder] = _wired_study_service
app.dependency_overrides[_card_repo_placeholder] = _wired_card_repository

# -- Routers ---------------------------------------------------------------

app.include_router(study_router)
app.include_router(card_router)


# -- Root / health ---------------------------------------------------------


@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to Easy SKS API"}


@app.get("/health", tags=["General"])
async def health_check():
    return {"status": "healthy"}
