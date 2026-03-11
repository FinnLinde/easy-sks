"""Application service for validating and transcribing answer recordings."""

from __future__ import annotations

from transcription.service.audio_transcriber_port import AudioTranscriberPort


class AudioTranscriptionUnavailableError(RuntimeError):
    """Raised when no transcription provider is configured."""


class AudioTranscriptionService:
    """Validates uploads before delegating to the provider adapter."""

    _ALLOWED_CONTENT_TYPES = frozenset(
        {
            "audio/mp4",
            "audio/mpeg",
            "audio/ogg",
            "audio/wav",
            "audio/webm",
            "video/mp4",
            "video/webm",
        }
    )

    def __init__(
        self,
        *,
        transcriber: AudioTranscriberPort | None,
        default_language: str,
        max_file_bytes: int,
    ) -> None:
        self._transcriber = transcriber
        self._default_language = default_language
        self._max_file_bytes = max_file_bytes

    async def transcribe_audio(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None,
        language: str | None,
    ) -> str:
        if self._transcriber is None:
            raise AudioTranscriptionUnavailableError(
                "Audio transcription is not configured. Set TRANSCRIPTION_OPENAI_API_KEY."
            )

        if not audio_bytes:
            raise ValueError("Audio file is empty.")
        if len(audio_bytes) > self._max_file_bytes:
            raise ValueError("Audio file exceeds the maximum allowed size.")

        normalized_content_type = _normalize_content_type(content_type)
        if (
            normalized_content_type is not None
            and normalized_content_type not in self._ALLOWED_CONTENT_TYPES
        ):
            raise ValueError("Unsupported audio format.")

        normalized_language = (language or self._default_language).strip().lower()
        if not normalized_language:
            normalized_language = self._default_language

        transcript = await self._transcriber.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=normalized_content_type,
            language=normalized_language,
        )
        if not transcript.strip():
            raise ValueError("No transcript could be generated from the recording.")
        return transcript.strip()


def _normalize_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None
    normalized = content_type.split(";", maxsplit=1)[0].strip().lower()
    return normalized or None
