"""FastAPI dependency factories for authentication and authorization."""

from __future__ import annotations

import functools
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, PyJWKClientError

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.token_verifier_port import TokenVerifierPort

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer()


@functools.lru_cache
def _get_verifier() -> TokenVerifierPort:
    """Lazily build the Cognito token verifier on first use.

    Lazy initialisation avoids hitting the JWKS endpoint (and requiring
    environment variables) at import time, which keeps test collection
    fast and side-effect-free.
    """
    from auth.service.auth_config import AuthConfig
    from auth.service.cognito_token_verifier import CognitoTokenVerifier

    return CognitoTokenVerifier(AuthConfig())


# -- Authentication dependency (global) ------------------------------------


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(_bearer_scheme)
    ],
) -> AuthenticatedUser:
    """Validate the Bearer token and return the authenticated user.

    Intended to be used as a **router-level** dependency so that every
    request on protected routers is authenticated automatically.
    """
    try:
        return _get_verifier().verify_token(credentials.credentials)
    except (InvalidTokenError, PyJWKClientError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# -- Authorization dependency factory (per-endpoint / per-router) ----------


def require_role(*roles: Role) -> Depends:
    """Return a FastAPI ``Depends`` that checks the user has at least one of *roles*.

    Usage::

        @router.get("/admin/users", dependencies=[require_role(Role.ADMIN)])
        async def list_users(): ...

    The inner callable is annotated with ``_required_roles`` so that the
    enforcement test can introspect it.
    """

    async def _check_role(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not any(user.has_role(r) for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    _check_role._required_roles = roles  # type: ignore[attr-defined]

    return Depends(_check_role)
