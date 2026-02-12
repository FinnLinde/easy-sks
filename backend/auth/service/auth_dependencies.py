"""FastAPI dependency factories for authentication and authorization."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.jwt_config import JwtConfig
from auth.service.jwt_service import JwtService

# -- Shared instances -------------------------------------------------------

_jwt_config = JwtConfig()
_jwt_service = JwtService(_jwt_config)
_bearer_scheme = HTTPBearer()


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
        return _jwt_service.decode_token(credentials.credentials)
    except InvalidTokenError:
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

    # Marker attribute used by the enforcement test to verify that every
    # protected route declares a required role.
    _check_role._required_roles = roles  # type: ignore[attr-defined]

    return Depends(_check_role)
