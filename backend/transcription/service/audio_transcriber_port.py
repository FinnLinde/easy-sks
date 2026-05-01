"""Port for converting recorded audio into plain text."""

from __future__ import annotations

from typing import Protocol


class AudioTranscriberPort(Protocol):
    """Abstracts the external speech-to-text provider."""

    async def transcribe_audio(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None,
        language: str,
    ) -> str:
        """Return a transcript for the provided audio payload."""
