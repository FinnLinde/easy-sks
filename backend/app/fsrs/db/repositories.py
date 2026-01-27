from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.fsrs.domain.enums import ReviewRating
from app.fsrs.domain.models import CardLearningProgress, CardReviewEvent

from .models import CardLearningProgressModel, CardReviewEventModel


def _to_domain_progress(model: CardLearningProgressModel) -> CardLearningProgress:
    return CardLearningProgress(
        user_id=model.user_id,
        card_id=model.card_id,
        stability=model.stability,
        difficulty=model.difficulty,
        due_at=model.due_at,
        last_reviewed_at=model.last_reviewed_at,
        state=model.state,
    )


def _to_domain_event(model: CardReviewEventModel) -> CardReviewEvent:
    return CardReviewEvent(
        user_id=model.user_id,
        card_id=model.card_id,
        reviewed_at=model.reviewed_at,
        rating=ReviewRating(model.rating),
    )


class SqlAlchemyProgressRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: UUID, card_id: UUID) -> CardLearningProgress | None:
        stmt = select(CardLearningProgressModel).where(
            CardLearningProgressModel.user_id == user_id,
            CardLearningProgressModel.card_id == card_id,
        )
        model = self._session.execute(stmt).scalars().first()
        return _to_domain_progress(model) if model else None

    def upsert(self, progress: CardLearningProgress) -> None:
        stmt = select(CardLearningProgressModel).where(
            CardLearningProgressModel.user_id == progress.user_id,
            CardLearningProgressModel.card_id == progress.card_id,
        )
        model = self._session.execute(stmt).scalars().first()
        if model is None:
            model = CardLearningProgressModel(
                user_id=progress.user_id,
                card_id=progress.card_id,
                stability=progress.stability,
                difficulty=progress.difficulty,
                due_at=progress.due_at,
                last_reviewed_at=progress.last_reviewed_at,
                state=progress.state,
            )
            self._session.add(model)
            return

        model.stability = progress.stability
        model.difficulty = progress.difficulty
        model.due_at = progress.due_at
        model.last_reviewed_at = progress.last_reviewed_at
        model.state = progress.state

    def list_due(
        self,
        user_id: UUID,
        now: datetime,
        limit: int,
        deck_id: UUID | None = None,
    ) -> list[CardLearningProgress]:
        stmt = (
            select(CardLearningProgressModel)
            .where(
                CardLearningProgressModel.user_id == user_id,
                CardLearningProgressModel.due_at <= now,
            )
            .order_by(CardLearningProgressModel.due_at)
            .limit(limit)
        )
        if deck_id is not None:
            # Deck filtering can be added once progress links to decks.
            pass
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain_progress(model) for model in models]


class SqlAlchemyReviewEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, event: CardReviewEvent) -> None:
        model = CardReviewEventModel(
            user_id=event.user_id,
            card_id=event.card_id,
            reviewed_at=event.reviewed_at,
            rating=int(event.rating),
        )
        self._session.add(model)

    def list_by_card(
        self,
        user_id: UUID,
        card_id: UUID,
        limit: int,
    ) -> list[CardReviewEvent]:
        stmt = (
            select(CardReviewEventModel)
            .where(
                CardReviewEventModel.user_id == user_id,
                CardReviewEventModel.card_id == card_id,
            )
            .order_by(CardReviewEventModel.reviewed_at.desc())
            .limit(limit)
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain_event(model) for model in models]
