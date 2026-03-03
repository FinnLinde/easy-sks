"""Configuration for AI-backed exam answer evaluation."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class ExamAiConfig(BaseSettings):
    """Environment-based settings for the exam evaluator."""

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 25.0

    model_config = {"env_prefix": "EXAM_AI_"}
