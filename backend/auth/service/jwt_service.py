"""JWT token decoding and validation."""

from __future__ import annotations

import jwt
from jwt.exceptions import InvalidTokenError

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.jwt_config import JwtConfig


class JwtService:
    """Decode and validate JWT tokens, returning an AuthenticatedUser."""

    def __init__(self, config: JwtConfig) -> None:
        self._config = config

    def decode_token(self, token: str) -> AuthenticatedUser:
        """Decode a JWT token and return the authenticated user.

        Raises ``InvalidTokenError`` on any validation failure
        (expired, bad signature, malformed, etc.).
        """
        decode_options: dict[str, object] = {
            "require": ["sub"],
        }

        kwargs: dict[str, object] = {
            "algorithms": [self._config.algorithm],
            "options": decode_options,
        }
        if self._config.audience is not None:
            kwargs["audience"] = self._config.audience
        if self._config.issuer is not None:
            kwargs["issuer"] = self._config.issuer

        payload: dict[str, object] = jwt.decode(
            token,
            self._config.secret_key,
            **kwargs,
        )

        user_id = str(payload["sub"])
        raw_roles = payload.get("roles", [])

        roles: list[Role] = []
        if isinstance(raw_roles, list):
            for r in raw_roles:
                try:
                    roles.append(Role(r))
                except ValueError:
                    pass  # ignore unknown roles

        return AuthenticatedUser(user_id=user_id, roles=roles)
