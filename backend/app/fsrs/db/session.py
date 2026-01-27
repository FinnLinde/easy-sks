from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_session_factory(
    database_url: str | None = None,
) -> sessionmaker[Session]:
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./fsrs.db")
    connect_args: dict[str, object] = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, future=True, connect_args=connect_args)
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
