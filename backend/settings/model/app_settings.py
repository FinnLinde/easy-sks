from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"


@dataclass
class AppSettings:
    """User-editable application settings (single row)."""

    ai_enabled: bool = False
    openai_api_key: str | None = None
    openai_chat_model: str = DEFAULT_CHAT_MODEL
    openai_transcription_model: str = DEFAULT_TRANSCRIPTION_MODEL

    @property
    def ai_ready(self) -> bool:
        """True when AI features can actually be used."""
        return self.ai_enabled and bool(self.openai_api_key)
