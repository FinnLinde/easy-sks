"""Role enum for role-based access control."""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """Roles that can be assigned to authenticated users."""

    FREEMIUM = "freemium"
    PREMIUM = "premium"
    ADMIN = "admin"
