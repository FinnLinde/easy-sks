"""Validation and normalization rules for user profile fields."""

from __future__ import annotations

import re

MIN_FULL_NAME_LENGTH = 2
MOBILE_NUMBER_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


class ProfileValidationError(ValueError):
    """Raised when submitted profile data violates domain rules."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_full_name(full_name: str) -> str:
    """Return a normalized full name or raise ``ProfileValidationError``."""
    normalized = " ".join(full_name.split())
    if len(normalized) < MIN_FULL_NAME_LENGTH:
        raise ProfileValidationError(
            code="invalid_full_name",
            message="Full name must contain at least two characters.",
        )
    return normalized


def normalize_mobile_number(mobile_number: str) -> str:
    """Return a normalized mobile number or raise ``ProfileValidationError``."""
    normalized = mobile_number.strip()
    if not MOBILE_NUMBER_PATTERN.fullmatch(normalized):
        raise ProfileValidationError(
            code="invalid_mobile_number",
            message="Mobile number must use international format like +49123456789.",
        )
    return normalized


def is_profile_complete(full_name: str | None, mobile_number: str | None) -> bool:
    """Return whether required profile fields are present and valid."""
    if full_name is None or mobile_number is None:
        return False

    try:
        normalize_full_name(full_name)
        normalize_mobile_number(mobile_number)
    except ProfileValidationError:
        return False

    return True
