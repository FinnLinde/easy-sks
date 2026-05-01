from __future__ import annotations

from dataclasses import dataclass

from card.model.card import Card
from scheduling.model.card_scheduling_info import CardSchedulingInfo


@dataclass(frozen=True)
class StudyCard:
    """Read-only view combining a card with its scheduling state."""

    card: Card
    scheduling_info: CardSchedulingInfo
