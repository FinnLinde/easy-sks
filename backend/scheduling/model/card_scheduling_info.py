from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from scheduling.model.card_state import CardState


@dataclass
class CardSchedulingInfo:
    """Holds the FSRS scheduling state for a card."""

    card_id: str = field(default_factory=lambda: str(uuid4()))
    state: CardState = CardState.NEW
    stability: float = 0.0
    difficulty: float = 0.0
    elapsed_days: int = 0
    scheduled_days: int = 0
    reps: int = 0
    lapses: int = 0
    due: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_review: datetime | None = None
