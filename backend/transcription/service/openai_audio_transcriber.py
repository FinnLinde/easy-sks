"""OpenAI-backed speech-to-text adapter."""

from __future__ import annotations

from io import BytesIO

from openai import AsyncOpenAI

from transcription.service.audio_transcriber_port import AudioTranscriberPort


class OpenAiAudioTranscriber(AudioTranscriberPort):
    """Transcribes short answer recordings with OpenAI."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def transcribe_audio(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None,
        language: str,
    ) -> str:
        audio_file = BytesIO(audio_bytes)
        audio_file.name = filename or "answer-recording.webm"

        transcription = await self._client.audio.transcriptions.create(
            model=self._model,
            file=audio_file,
            language=language,
            timeout=self._timeout_seconds,
        )
        return (transcription.text or "").strip()
