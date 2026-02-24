"""Centralised authentication configuration loaded from environment variables."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    """AWS Cognito authentication settings.

    All environments (production and local development) authenticate
    against Cognito.  Use the *prod* app client in production and the
    *local-dev* app client for local development.

    Environment variables are prefixed with ``AUTH_``, e.g.
    ``AUTH_COGNITO_USER_POOL_ID``, ``AUTH_COGNITO_REGION``.
    """

    cognito_user_pool_id: Optional[str] = None
    cognito_region: Optional[str] = None
    cognito_app_client_id: Optional[str] = None

    model_config = {"env_prefix": "AUTH_"}
