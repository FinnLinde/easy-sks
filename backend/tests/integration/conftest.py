"""Fixtures for integration tests.

Spins up a PostgreSQL testcontainer and provides:
- An async SQLAlchemy session (function-scoped, rolled back per test)
- A FastAPI test client wired to that session
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from database import Base


# ---------------------------------------------------------------------------
# Sync / session-scoped fixtures (no event-loop issues)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for the entire test session."""
    with PostgresContainer("postgres:17") as pg:
        yield pg


@pytest.fixture(scope="session")
def postgres_url(postgres_container) -> str:
    """Derive the asyncpg connection URL from the running container."""
    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session", autouse=True)
def _create_tables(postgres_url: str):
    """Create all tables once at the start of the session (sync wrapper)."""

    async def _do_create() -> None:
        eng = create_async_engine(postgres_url, echo=False)

        # Import table modules so Base.metadata knows about them
        import card.db.card_table  # noqa: F401
        import scheduling.db.review_log_table  # noqa: F401
        import scheduling.db.scheduling_table  # noqa: F401

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await eng.dispose()

    asyncio.run(_do_create())


# ---------------------------------------------------------------------------
# Function-scoped async fixtures (each test gets its own loop + session)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session(
    postgres_url: str,
) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional async session that is rolled back after each test."""
    eng = create_async_engine(postgres_url, echo=False)
    factory = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        yield session
        await session.rollback()

    await eng.dispose()


@pytest_asyncio.fixture
async def client(
    postgres_url: str, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient wired to the FastAPI app with the test DB."""
    from dependencies import get_db_session
    from main import app

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_db_session, None)
