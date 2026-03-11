"""Integration tests for the audio transcription API endpoint."""

from __future__ import annotations

import pytest

from transcription.service.audio_transcription_service import (
    AudioTranscriptionUnavailableError,
)


class _FakeTranscriptionService:
    async def transcribe_audio(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None,
        language: str | None,
    ) -> str:
        assert audio_bytes == b"fake-audio"
        assert filename == "answer.webm"
        assert content_type == "audio/webm"
        assert language == "de"
        return "Das ist ein Testtranskript."


class _RejectingTranscriptionService:
    async def transcribe_audio(self, **kwargs) -> str:
        raise ValueError("Unsupported audio format.")


class _UnavailableTranscriptionService:
    async def transcribe_audio(self, **kwargs) -> str:
        raise AudioTranscriptionUnavailableError(
            "Audio transcription is not configured. Set TRANSCRIPTION_OPENAI_API_KEY."
        )


class _BrokenTranscriptionService:
    async def transcribe_audio(self, **kwargs) -> str:
        raise RuntimeError("upstream provider rejected audio")


@pytest.mark.asyncio
class TestTranscriptionApi:
    async def test_transcribes_uploaded_audio(self, client):
        from main import app
        from transcription.controller.transcription_controller import (
            get_audio_transcription_service,
        )

        app.dependency_overrides[get_audio_transcription_service] = (
            lambda: _FakeTranscriptionService()
        )
        try:
            response = await client.post(
                "/ai/transcribe-audio",
                files={"audio": ("answer.webm", b"fake-audio", "audio/webm")},
                data={"language": "de"},
            )
        finally:
            app.dependency_overrides.pop(get_audio_transcription_service, None)

        assert response.status_code == 200
        assert response.json() == {"transcript": "Das ist ein Testtranskript."}

    async def test_returns_400_for_invalid_audio(self, client):
        from main import app
        from transcription.controller.transcription_controller import (
            get_audio_transcription_service,
        )

        app.dependency_overrides[get_audio_transcription_service] = (
            lambda: _RejectingTranscriptionService()
        )
        try:
            response = await client.post(
                "/ai/transcribe-audio",
                files={"audio": ("answer.txt", b"fake-audio", "text/plain")},
            )
        finally:
            app.dependency_overrides.pop(get_audio_transcription_service, None)

        assert response.status_code == 400
        assert response.json()["detail"] == "Unsupported audio format."

    async def test_returns_503_when_transcription_is_unavailable(self, client):
        from main import app
        from transcription.controller.transcription_controller import (
            get_audio_transcription_service,
        )

        app.dependency_overrides[get_audio_transcription_service] = (
            lambda: _UnavailableTranscriptionService()
        )
        try:
            response = await client.post(
                "/ai/transcribe-audio",
                files={"audio": ("answer.webm", b"fake-audio", "audio/webm")},
            )
        finally:
            app.dependency_overrides.pop(get_audio_transcription_service, None)

        assert response.status_code == 503
        assert (
            response.json()["detail"]
            == "Audio transcription is not configured. Set TRANSCRIPTION_OPENAI_API_KEY."
        )

    async def test_returns_upstream_error_details_for_unexpected_failures(self, client):
        from main import app
        from transcription.controller.transcription_controller import (
            get_audio_transcription_service,
        )

        app.dependency_overrides[get_audio_transcription_service] = (
            lambda: _BrokenTranscriptionService()
        )
        try:
            response = await client.post(
                "/ai/transcribe-audio",
                files={"audio": ("answer.webm", b"fake-audio", "audio/webm")},
            )
        finally:
            app.dependency_overrides.pop(get_audio_transcription_service, None)

        assert response.status_code == 503
        assert (
            response.json()["detail"]
            == "Audio transcription failed: upstream provider rejected audio"
        )
