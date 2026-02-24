"""AWS Cognito token verifier using JWKS (RS256)."""

from __future__ import annotations

import jwt
from jwt import PyJWKClient

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.auth_config import AuthConfig
from auth.service.token_verifier_port import TokenVerifierPort


class CognitoTokenVerifier(TokenVerifierPort):
    """Validate JWTs issued by an AWS Cognito User Pool.

    Tokens are verified against Cognito's public JWKS endpoint using RS256.
    The ``PyJWKClient`` caches the key set automatically, so repeated calls
    do not trigger a network request on every token verification.
    """

    def __init__(self, config: AuthConfig) -> None:
        if not config.cognito_user_pool_id or not config.cognito_region:
            raise ValueError(
                "cognito_user_pool_id and cognito_region are required "
                "when AUTH_PROVIDER=cognito"
            )

        self._app_client_id = config.cognito_app_client_id
        self._issuer = (
            f"https://cognito-idp.{config.cognito_region}.amazonaws.com"
            f"/{config.cognito_user_pool_id}"
        )
        jwks_url = f"{self._issuer}/.well-known/jwks.json"
        self._jwk_client = PyJWKClient(jwks_url)

    def verify_token(self, token: str) -> AuthenticatedUser:
        signing_key = self._jwk_client.get_signing_key_from_jwt(token)

        decode_kwargs: dict[str, object] = {
            "algorithms": ["RS256"],
            "issuer": self._issuer,
            "options": {"require": ["sub", "iss", "exp"]},
        }
        if self._app_client_id is not None:
            decode_kwargs["audience"] = self._app_client_id

        payload: dict[str, object] = jwt.decode(
            token,
            signing_key.key,
            **decode_kwargs,
        )

        user_id = str(payload["sub"])
        raw_groups = payload.get("cognito:groups", [])

        roles: list[Role] = []
        if isinstance(raw_groups, list):
            for group in raw_groups:
                try:
                    roles.append(Role(group))
                except ValueError:
                    pass

        return AuthenticatedUser(user_id=user_id, roles=roles)
