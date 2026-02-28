"""Local application user model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from user.model.profile_validation import is_profile_complete


@dataclass(frozen=True)
class AppUser:
    """Represents a persisted local EasySKS user."""

    id: str
    auth_provider: str
    auth_provider_user_id: str
    email: str | None
    full_name: str | None
    mobile_number: str | None
    mobile_verified_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @property
    def profile_complete(self) -> bool:
        """Return whether the profile has all required onboarding fields."""
        return is_profile_complete(self.full_name, self.mobile_number)
