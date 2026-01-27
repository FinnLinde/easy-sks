from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends

from app.fsrs.service.use_cases import get_due_queue, grade_card

from .deps import get_scheduler, get_uow
from .schemas import (
    CardLearningProgressResponse,
    ReviewRequest,
    progress_to_response,
)

router = APIRouter(tags=["fsrs"])


@router.get("/queue", response_model=list[CardLearningProgressResponse])
def queue(
    user_id: UUID,
    limit: int = 50,
    now: datetime | None = None,
    uow=Depends(get_uow),
) -> list[CardLearningProgressResponse]:
    timestamp = now or datetime.now(timezone.utc)
    progress_items = get_due_queue(uow, user_id, timestamp, limit)
    return [progress_to_response(progress) for progress in progress_items]


@router.post("/reviews", response_model=CardLearningProgressResponse)
def review(
    payload: ReviewRequest,
    uow=Depends(get_uow),
    scheduler=Depends(get_scheduler),
) -> CardLearningProgressResponse:
    updated = grade_card(
        uow=uow,
        scheduler=scheduler,
        user_id=payload.user_id,
        card_id=payload.card_id,
        rating=payload.rating,
        reviewed_at=payload.reviewed_at,
    )
    return progress_to_response(updated)
