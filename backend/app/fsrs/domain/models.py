from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .enums import CardState, ReviewRating


@dataclass
class CardLearningProgress:
    user_id: UUID
    card_id: UUID
    stability: float
    difficulty: float
    due_at: datetime
    last_reviewed_at: datetime | None
    state: CardState


@dataclass
class CardReviewEvent:
    user_id: UUID
    card_id: UUID
    reviewed_at: datetime
    rating: ReviewRating
