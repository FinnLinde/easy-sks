"""Local application user model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AppUser:
    """Represents a persisted local EasySKS user."""

    id: str
    auth_provider: str
    auth_provider_user_id: str
    email: str | None
    created_at: datetime
    updated_at: datetime

