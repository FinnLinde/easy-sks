"""Application service for managing cards and their images.

Image storage is delegated to an ImageStoragePort adapter,
keeping the service decoupled from any specific cloud provider.
"""

from __future__ import annotations

from card.model.card import Card
from card.model.card_content import CardContent
from card.model.card_image import CardImage
from card.service.image_storage_port import ImageStoragePort


class CardService:
    """Provides operations for creating cards and managing card images."""

    def __init__(self, image_storage: ImageStoragePort) -> None:
        self._image_storage = image_storage

    def create_card(
        self,
        front: CardContent,
        answer: CardContent,
        short_answer: CardContent,
        tags: list[str] | None = None,
    ) -> Card:
        """Create a new card with the given content and tags."""
        return Card(
            front=front,
            answer=answer,
            short_answer=short_answer,
            tags=tags or [],
        )

    def add_image_to_content(
        self,
        content: CardContent,
        image_data: bytes,
        content_type: str,
    ) -> CardContent:
        """Upload an image and return a new CardContent with it appended."""
        storage_key = self._image_storage.upload(image_data, content_type)
        image = CardImage(storage_key=storage_key)
        return CardContent(
            text=content.text,
            images=[*content.images, image],
        )

    def get_image_url(self, image: CardImage) -> str:
        """Return a URL for accessing the given image."""
        return self._image_storage.get_url(image.storage_key)
