from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from scheduling.model.rating import Rating


@dataclass
class ReviewLog:
    """Records a single review event for a card."""

    card_id: str
    rating: Rating
    reviewed_at: datetime
    review_duration_ms: int | None = None
