from __future__ import annotations

from typing import Protocol


class ImageStoragePort(Protocol):
    """Port for storing and retrieving images in cloud storage."""

    def upload(self, image_data: bytes, content_type: str) -> str:
        """Upload image data and return the storage key."""
        ...

    def get_url(self, storage_key: str) -> str:
        """Return a URL for accessing the image at the given storage key."""
        ...

    def delete(self, storage_key: str) -> None:
        """Delete the image at the given storage key."""
        ...
