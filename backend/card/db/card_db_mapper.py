"""Maps between Card domain objects and CardRow ORM objects."""

from __future__ import annotations

from card.db.card_table import CardRow
from card.model.card import Card
from card.model.card_content import CardContent
from card.model.card_image import CardImage


class CardDbMapper:
    """Stateless mapper between Card domain objects and database rows."""

    @staticmethod
    def to_domain(row: CardRow) -> Card:
        """Convert a CardRow to a Card domain object."""
        return Card(
            card_id=row.card_id,
            front=CardContent(
                text=row.front_text,
                images=[
                    CardImage(
                        storage_key=img["storage_key"],
                        image_id=img.get("image_id", ""),
                        alt_text=img.get("alt_text"),
                    )
                    for img in (row.front_images or [])
                ],
            ),
            answer=CardContent(
                text=row.answer_text,
                images=[
                    CardImage(
                        storage_key=img["storage_key"],
                        image_id=img.get("image_id", ""),
                        alt_text=img.get("alt_text"),
                    )
                    for img in (row.answer_images or [])
                ],
            ),
            short_answer=row.short_answer or [],
            tags=list(row.tags) if row.tags else [],
        )

    @staticmethod
    def to_row(card: Card) -> CardRow:
        """Convert a Card domain object to a CardRow."""
        return CardRow(
            card_id=card.card_id,
            front_text=card.front.text,
            front_images=[
                {
                    "storage_key": img.storage_key,
                    "image_id": img.image_id,
                    "alt_text": img.alt_text,
                }
                for img in card.front.images
            ],
            answer_text=card.answer.text,
            answer_images=[
                {
                    "storage_key": img.storage_key,
                    "image_id": img.image_id,
                    "alt_text": img.alt_text,
                }
                for img in card.answer.images
            ],
            short_answer=card.short_answer,
            tags=card.tags,
        )
