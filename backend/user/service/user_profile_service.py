"""Application service for user profile management."""

from __future__ import annotations

from user.db.user_repository import MobileNumberConflictError, UserRepository
from user.model.app_user import AppUser
from user.model.profile_validation import (
    ProfileValidationError,
    normalize_full_name,
    normalize_mobile_number,
)


class MobileNumberInUseError(ValueError):
    """Raised when a mobile number is already assigned to another account."""


class UserProfileService:
    """Coordinates profile validation and persistence."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def update_profile(
        self, user_id: str, full_name: str, mobile_number: str
    ) -> AppUser:
        normalized_full_name = normalize_full_name(full_name)
        normalized_mobile_number = normalize_mobile_number(mobile_number)

        try:
            return await self._user_repository.update_profile(
                user_id=user_id,
                full_name=normalized_full_name,
                mobile_number=normalized_mobile_number,
            )
        except MobileNumberConflictError as exc:
            raise MobileNumberInUseError("mobile_number_in_use") from exc


__all__ = [
    "MobileNumberInUseError",
    "ProfileValidationError",
    "UserProfileService",
]
