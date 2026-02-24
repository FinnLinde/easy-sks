"""Abstract interface for token verification."""

from __future__ import annotations

from abc import ABC, abstractmethod

from auth.model.authenticated_user import AuthenticatedUser


class TokenVerifierPort(ABC):
    """Port that decouples authentication logic from a specific JWT provider.

    Implementations handle provider-specific token validation (e.g. Cognito
    JWKS, local HS256) and return a unified ``AuthenticatedUser``.
    """

    @abstractmethod
    def verify_token(self, token: str) -> AuthenticatedUser:
        """Validate *token* and return the authenticated identity.

        Raises ``jwt.exceptions.InvalidTokenError`` (or a subclass) when
        the token is invalid, expired, or cannot be verified.
        """
