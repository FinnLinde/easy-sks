"""JWT configuration loaded from environment variables."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class JwtConfig(BaseSettings):
    """Provider-agnostic JWT settings.

    All values can be overridden via environment variables prefixed with
    ``JWT_``, e.g. ``JWT_SECRET_KEY``, ``JWT_ALGORITHM``.

    To switch to an external provider later, change the secret / algorithm
    and optionally set audience / issuer.
    """

    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    audience: Optional[str] = None
    issuer: Optional[str] = None

    model_config = {"env_prefix": "JWT_"}
