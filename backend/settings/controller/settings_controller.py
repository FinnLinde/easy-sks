"""FastAPI router for application settings."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from settings.model.app_settings import AppSettings
from settings.service.settings_service import SettingsService

router = APIRouter(tags=["Settings"])


class SettingsOut(BaseModel):
    ai_enabled: bool
    openai_api_key_set: bool
    openai_chat_model: str
    openai_transcription_model: str


class SettingsIn(BaseModel):
    """Request body for `PUT /settings`.

    `openai_api_key` semantics: omit to leave unchanged; pass `null` or `""`
    to clear the stored key; pass a string to replace it.
    """

    ai_enabled: bool | None = None
    openai_api_key: str | None = None
    openai_chat_model: str | None = None
    openai_transcription_model: str | None = None


def _to_out(settings: AppSettings) -> SettingsOut:
    return SettingsOut(
        ai_enabled=settings.ai_enabled,
        openai_api_key_set=bool(settings.openai_api_key),
        openai_chat_model=settings.openai_chat_model,
        openai_transcription_model=settings.openai_transcription_model,
    )


def get_settings_service() -> SettingsService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


@router.get("/settings", response_model=SettingsOut)
async def get_settings(
    service: SettingsService = Depends(get_settings_service),
) -> SettingsOut:
    return _to_out(await service.get())


@router.put("/settings", response_model=SettingsOut)
async def update_settings(
    body: SettingsIn,
    service: SettingsService = Depends(get_settings_service),
) -> SettingsOut:
    fields_provided = body.model_fields_set

    if "openai_api_key" in fields_provided:
        raw_key = body.openai_api_key
        if raw_key is None or raw_key == "":
            api_key_arg: str | None = None
            clear_key = True
        else:
            api_key_arg = raw_key
            clear_key = False
    else:
        api_key_arg = None
        clear_key = False

    updated = await service.update(
        ai_enabled=body.ai_enabled,
        openai_api_key=api_key_arg,
        clear_openai_api_key=clear_key,
        openai_chat_model=body.openai_chat_model,
        openai_transcription_model=body.openai_transcription_model,
    )
    return _to_out(updated)
