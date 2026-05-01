from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubQuestion:
    """A single sub-question within a navigation task."""

    text: str
    points: int = 1


@dataclass
class NavigationTask:
    """A navigation exam task with context, sub-questions, and reference solution."""

    task_id: str
    sheet_number: int
    task_number: int
    points: int
    context: str
    sub_questions: list[SubQuestion] = field(default_factory=list)
    solution_text: str = ""
    key_answers: list[str] = field(default_factory=list)
