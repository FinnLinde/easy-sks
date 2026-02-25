"""Authenticated user identity extracted from a JWT token."""

from __future__ import annotations

from dataclasses import dataclass

from auth.model.role import Role


@dataclass(frozen=True)
class AuthenticatedUser:
    """Represents the identity of an authenticated user."""

    user_id: str
    roles: list[Role]
    email: str | None = None

    def has_role(self, role: Role) -> bool:
        """Check whether the user has a specific role."""
        return role in self.roles
