from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class CardImage:
    """Represents a reference to an image stored in cloud storage."""

    storage_key: str
    image_id: str = field(default_factory=lambda: str(uuid4()))
    alt_text: str | None = None
