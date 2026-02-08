from __future__ import annotations

from dataclasses import dataclass, field

from card.model.card_image import CardImage


@dataclass
class CardContent:
    """A piece of card content combining text and optional images."""

    text: str = ""
    images: list[CardImage] = field(default_factory=list)
