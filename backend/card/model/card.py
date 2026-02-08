from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from card.model.card_content import CardContent


@dataclass
class Card:
    """A flashcard with a front, answer, short answer, and tags."""

    card_id: str = field(default_factory=lambda: str(uuid4()))
    front: CardContent = field(default_factory=CardContent)
    answer: CardContent = field(default_factory=CardContent)
    short_answer: CardContent = field(default_factory=CardContent)
    tags: list[str] = field(default_factory=list)
