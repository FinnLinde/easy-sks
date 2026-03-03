from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExamTemplate:
    """Metadata for a supported official SKS exam sheet."""

    sheet_number: int
    display_name: str
    question_count: int
    time_limit_minutes: int
