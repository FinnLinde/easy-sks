from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.fsrs.domain.enums import CardState, ReviewRating
from app.fsrs.domain.models import CardLearningProgress


class ReviewRequest(BaseModel):
    user_id: UUID
    card_id: UUID
    rating: ReviewRating
    reviewed_at: datetime | None = None


class CardLearningProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    card_id: UUID
    stability: float
    difficulty: float
    due_at: datetime
    last_reviewed_at: datetime | None
    state: CardState


def progress_to_response(
    progress: CardLearningProgress,
) -> CardLearningProgressResponse:
    return CardLearningProgressResponse(
        user_id=progress.user_id,
        card_id=progress.card_id,
        stability=progress.stability,
        difficulty=progress.difficulty,
        due_at=progress.due_at,
        last_reviewed_at=progress.last_reviewed_at,
        state=progress.state,
    )
