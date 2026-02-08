"""Application service that orchestrates the card and scheduling domains.

All cross-domain composition lives here -- neither the card nor the
scheduling domain imports from the other.
"""

from __future__ import annotations

from datetime import datetime, timezone

from scheduling.model.rating import Rating
from scheduling.service.scheduling_service import SchedulingService

from study.model.sks_topic import SksTopic
from study.model.study_card import StudyCard
from study.service.card_repository_port import CardRepositoryPort
from study.service.scheduling_repository_port import SchedulingRepositoryPort


class StudyService:
    """Provides study operations by composing card and scheduling domains."""

    def __init__(
        self,
        card_repo: CardRepositoryPort,
        scheduling_repo: SchedulingRepositoryPort,
        scheduling_service: SchedulingService,
    ) -> None:
        self._card_repo = card_repo
        self._scheduling_repo = scheduling_repo
        self._scheduling_service = scheduling_service

    async def get_due_cards(
        self, topic: SksTopic | None = None
    ) -> list[StudyCard]:
        """Return cards that are due for review, optionally filtered by SKS topic."""
        now = datetime.now(timezone.utc)
        due_infos = await self._scheduling_repo.get_due(before=now)

        study_cards: list[StudyCard] = []
        for info in due_infos:
            card = await self._card_repo.get_by_id(info.card_id)
            if card is None:
                continue
            if topic is not None and topic.value not in card.tags:
                continue
            study_cards.append(StudyCard(card=card, scheduling_info=info))

        return study_cards

    async def review_card(self, card_id: str, rating: Rating) -> StudyCard:
        """Review a card and persist the updated scheduling state."""
        scheduling_info = await self._scheduling_repo.get_by_card_id(card_id)
        if scheduling_info is None:
            raise ValueError(f"No scheduling info found for card {card_id!r}")

        updated_info, _review_log = self._scheduling_service.review_card(
            scheduling_info, rating
        )
        await self._scheduling_repo.save(updated_info)

        card = await self._card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(f"Card {card_id!r} not found")

        return StudyCard(card=card, scheduling_info=updated_info)
