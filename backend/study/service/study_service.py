"""Application service that orchestrates the card and scheduling domains.

All cross-domain composition lives here -- neither the card nor the
scheduling domain imports from the other.
"""

from __future__ import annotations

from datetime import datetime, timezone

from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.rating import Rating
from scheduling.service.scheduling_service import SchedulingService

from study.model.sks_topic import SksTopic
from study.model.study_card import StudyCard
from study.service.card_repository_port import CardRepositoryPort
from study.service.scheduling_repository_port import SchedulingRepositoryPort

DEFAULT_NEW_CARD_LIMIT_PER_QUEUE = 20


class StudyService:
    """Provides study operations by composing card and scheduling domains."""

    def __init__(
        self,
        card_repo: CardRepositoryPort,
        scheduling_repo: SchedulingRepositoryPort,
        scheduling_service: SchedulingService,
        new_card_limit_per_queue: int = DEFAULT_NEW_CARD_LIMIT_PER_QUEUE,
    ) -> None:
        self._card_repo = card_repo
        self._scheduling_repo = scheduling_repo
        self._scheduling_service = scheduling_service
        self._new_card_limit_per_queue = max(0, new_card_limit_per_queue)

    async def get_due_cards(
        self, user_id: str, topic: SksTopic | None = None
    ) -> list[StudyCard]:
        """Return a due-first study queue, optionally filtered by topic."""
        now = datetime.now(timezone.utc)
        due_infos = await self._scheduling_repo.get_due_for_user(
            user_id=user_id, before=now
        )

        # Preserve repository order so /study/due remains deterministic.
        study_cards: list[StudyCard] = []
        for info in due_infos:
            card = await self._card_repo.get_by_id(info.card_id)
            if card is None:
                continue
            if topic is not None and topic.value not in card.tags:
                continue
            study_cards.append(StudyCard(card=card, scheduling_info=info))

        # Fill the queue with newly introduced cards, but cap how many "new"
        # cards are created at once so first-time users are not overwhelmed.
        new_card_slots = max(0, self._new_card_limit_per_queue - len(study_cards))
        if new_card_slots == 0:
            return study_cards

        new_cards = await self._introduce_new_cards(
            user_id=user_id,
            topic=topic,
            limit=new_card_slots,
        )
        return study_cards + new_cards

    async def get_practice_cards(
        self, user_id: str, topic: SksTopic | None = None
    ) -> list[StudyCard]:
        """Return a practice queue (due-first, then non-due scheduled cards)."""
        due_first = await self.get_due_cards(user_id=user_id, topic=topic)
        if len(due_first) >= self._new_card_limit_per_queue:
            return due_first

        queue = list(due_first)
        seen_card_ids = {sc.card.card_id for sc in queue}
        remaining = self._new_card_limit_per_queue - len(queue)

        all_infos = await self._scheduling_repo.list_for_user(user_id=user_id)
        all_infos_sorted = sorted(
            all_infos,
            key=lambda i: (
                i.due,
                i.last_review or datetime.min.replace(tzinfo=timezone.utc),
                i.card_id,
            ),
        )

        for info in all_infos_sorted:
            if remaining <= 0:
                break
            if info.card_id in seen_card_ids:
                continue
            card = await self._card_repo.get_by_id(info.card_id)
            if card is None:
                continue
            if topic is not None and topic.value not in card.tags:
                continue
            queue.append(StudyCard(card=card, scheduling_info=info))
            seen_card_ids.add(info.card_id)
            remaining -= 1

        if remaining <= 0:
            return queue

        introduced = await self._introduce_new_cards(
            user_id=user_id,
            topic=topic,
            limit=remaining,
        )
        return queue + introduced

    async def _introduce_new_cards(
        self,
        user_id: str,
        topic: SksTopic | None,
        limit: int,
    ) -> list[StudyCard]:
        """Create missing scheduling rows for up to *limit* new cards."""
        if limit <= 0:
            return []

        candidates = (
            await self._card_repo.get_by_tags([topic.value])
            if topic is not None
            else await self._card_repo.list_all()
        )

        introduced: list[StudyCard] = []
        for card in candidates:
            if len(introduced) >= limit:
                break

            existing = await self._scheduling_repo.get_by_user_and_card_id(
                user_id=user_id,
                card_id=card.card_id,
            )
            if existing is not None:
                continue

            info = CardSchedulingInfo(
                user_id=user_id,
                card_id=card.card_id,
            )
            await self._scheduling_repo.save(info)
            introduced.append(StudyCard(card=card, scheduling_info=info))

        return introduced

    async def review_card(
        self, user_id: str, card_id: str, rating: Rating
    ) -> StudyCard:
        """Review a card and persist scheduling + review log in one unit of work."""
        scheduling_info = await self._scheduling_repo.get_by_user_and_card_id(
            user_id=user_id, card_id=card_id
        )
        if scheduling_info is None:
            raise ValueError(f"No scheduling info found for card {card_id!r}")

        card = await self._card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(f"Card {card_id!r} not found")

        updated_info, review_log = self._scheduling_service.review_card(
            scheduling_info, rating
        )
        # Both writes use the same DB session in the adapter layer. FastAPI's
        # DB dependency commits/rolls back once per request for transactional
        # consistency between scheduling state and review history.
        await self._scheduling_repo.save(updated_info)
        await self._scheduling_repo.save_review_log(review_log)

        return StudyCard(card=card, scheduling_info=updated_info)
