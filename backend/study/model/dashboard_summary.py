"""Domain model for dashboard aggregate metrics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DashboardSummary:
    due_now: int
    reviewed_today: int
    streak_days: int
    due_by_topic: dict[str, int]
    recommended_topic: str | None
    available_cards: int
