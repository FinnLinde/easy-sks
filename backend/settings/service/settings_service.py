from __future__ import annotations

from settings.db.settings_repository import SettingsRepository
from settings.model.app_settings import AppSettings


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repo = repository

    async def get(self) -> AppSettings:
        return await self._repo.get()

    async def update(
        self,
        *,
        ai_enabled: bool | None = None,
        openai_api_key: str | None = None,
        clear_openai_api_key: bool = False,
        openai_chat_model: str | None = None,
        openai_transcription_model: str | None = None,
    ) -> AppSettings:
        current = await self._repo.get()

        if clear_openai_api_key:
            new_key: str | None = None
        elif openai_api_key is not None:
            new_key = openai_api_key.strip() or None
        else:
            new_key = current.openai_api_key

        updated = AppSettings(
            ai_enabled=current.ai_enabled if ai_enabled is None else ai_enabled,
            openai_api_key=new_key,
            openai_chat_model=(
                current.openai_chat_model
                if openai_chat_model is None
                else (openai_chat_model.strip() or current.openai_chat_model)
            ),
            openai_transcription_model=(
                current.openai_transcription_model
                if openai_transcription_model is None
                else (
                    openai_transcription_model.strip()
                    or current.openai_transcription_model
                )
            ),
        )
        return await self._repo.upsert(updated)
