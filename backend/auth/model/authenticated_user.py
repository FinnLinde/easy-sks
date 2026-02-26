"""Authenticated user identity extracted from a JWT token."""

from __future__ import annotations

from dataclasses import dataclass

from auth.model.role import Role

_ROLE_IMPLICATIONS: dict[Role, set[Role]] = {
    Role.FREEMIUM: {Role.FREEMIUM},
    Role.PREMIUM: {Role.PREMIUM, Role.FREEMIUM},
    Role.ADMIN: {Role.ADMIN, Role.PREMIUM, Role.FREEMIUM},
}


@dataclass(frozen=True)
class AuthenticatedUser:
    """Represents the identity of an authenticated user."""

    user_id: str
    roles: list[Role]
    email: str | None = None

    def has_role(self, role: Role) -> bool:
        """Check whether the user has a specific role (with hierarchy)."""
        return any(role in _ROLE_IMPLICATIONS.get(user_role, {user_role}) for user_role in self.roles)
