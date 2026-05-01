"""Repository for the single-row app_settings record."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from settings.db.settings_table import SETTINGS_ROW_ID, AppSettingsRow
from settings.model.app_settings import (
    DEFAULT_CHAT_MODEL,
    DEFAULT_TRANSCRIPTION_MODEL,
    AppSettings,
)


def _row_to_domain(row: AppSettingsRow) -> AppSettings:
    return AppSettings(
        ai_enabled=row.ai_enabled,
        openai_api_key=row.openai_api_key or None,
        openai_chat_model=row.openai_chat_model or DEFAULT_CHAT_MODEL,
        openai_transcription_model=(
            row.openai_transcription_model or DEFAULT_TRANSCRIPTION_MODEL
        ),
    )


class SettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> AppSettings:
        row = await self._session.get(AppSettingsRow, SETTINGS_ROW_ID)
        if row is None:
            row = AppSettingsRow(id=SETTINGS_ROW_ID)
            self._session.add(row)
            await self._session.flush()
        return _row_to_domain(row)

    async def upsert(self, settings: AppSettings) -> AppSettings:
        row = await self._session.get(AppSettingsRow, SETTINGS_ROW_ID)
        if row is None:
            row = AppSettingsRow(id=SETTINGS_ROW_ID)
            self._session.add(row)

        row.ai_enabled = settings.ai_enabled
        row.openai_api_key = settings.openai_api_key
        row.openai_chat_model = settings.openai_chat_model
        row.openai_transcription_model = settings.openai_transcription_model
        await self._session.flush()
        return _row_to_domain(row)
