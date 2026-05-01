"""SQLAlchemy ORM model for the single-row ``app_settings`` table."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from settings.model.app_settings import (
    DEFAULT_CHAT_MODEL,
    DEFAULT_TRANSCRIPTION_MODEL,
)

SETTINGS_ROW_ID = 1


class AppSettingsRow(Base):
    """Single-row settings table; ``id`` is always 1."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=SETTINGS_ROW_ID)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    openai_api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    openai_chat_model: Mapped[str] = mapped_column(
        String(128), nullable=False, default=DEFAULT_CHAT_MODEL
    )
    openai_transcription_model: Mapped[str] = mapped_column(
        String(128), nullable=False, default=DEFAULT_TRANSCRIPTION_MODEL
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
