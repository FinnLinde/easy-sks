"""FastAPI router for speech transcription endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from auth.model.role import Role
from auth.service.auth_dependencies import require_role
from transcription.service.audio_transcription_service import (
    AudioTranscriptionService,
    AudioTranscriptionUnavailableError,
)

router = APIRouter(tags=["AI"], dependencies=[require_role(Role.FREEMIUM)])
logger = logging.getLogger(__name__)


class AudioTranscriptionOut(BaseModel):
    transcript: str


def get_audio_transcription_service() -> AudioTranscriptionService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


@router.post("/ai/transcribe-audio", response_model=AudioTranscriptionOut)
async def transcribe_audio(
    audio: Annotated[UploadFile, File(...)],
    language: Annotated[str, Form()] = "de",
    transcription_service: AudioTranscriptionService = Depends(
        get_audio_transcription_service
    ),
) -> AudioTranscriptionOut:
    try:
        audio_bytes = await audio.read()
        transcript = await transcription_service.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename or "answer-recording.webm",
            content_type=audio.content_type,
            language=language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AudioTranscriptionUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception(
            "Audio transcription failed for filename=%s content_type=%s",
            audio.filename,
            audio.content_type,
        )
        raise HTTPException(
            status_code=503,
            detail=f"Audio transcription failed: {exc}",
        ) from exc
    finally:
        await audio.close()

    return AudioTranscriptionOut(transcript=transcript)
