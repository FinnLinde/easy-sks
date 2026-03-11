"""Environment-based settings for speech transcription."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class TranscriptionConfig(BaseSettings):
    """Configuration for the OpenAI transcription adapter."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini-transcribe"
    openai_timeout_seconds: float = 30.0
    default_language: str = "de"
    max_file_bytes: int = 10 * 1024 * 1024

    model_config = {"env_prefix": "TRANSCRIPTION_"}
