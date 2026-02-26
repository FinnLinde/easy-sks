"""AWS Cognito token verifier using JWKS (RS256)."""

from __future__ import annotations

import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError

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

        payload: dict[str, object] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=self._issuer,
            options={"require": ["sub", "iss", "exp"]},
        )

        # Frontend API calls should present a Cognito access token. Cognito
        # access tokens carry ``token_use=access`` and ``client_id`` (not ``aud``).
        token_use = payload.get("token_use")
        if token_use != "access":
            raise InvalidTokenError("Expected Cognito access token")

        if self._app_client_id is not None:
            client_id = payload.get("client_id")
            if client_id != self._app_client_id:
                raise InvalidTokenError("Token was not issued for this app client")

        user_id = str(payload["sub"])
        raw_groups = payload.get("cognito:groups", [])

        roles: list[Role] = []
        if isinstance(raw_groups, list):
            for group in raw_groups:
                try:
                    roles.append(Role(group))
                except ValueError:
                    pass

        return AuthenticatedUser(
            user_id=user_id,
            roles=roles,
            email=(
                str(payload["email"])
                if isinstance(payload.get("email"), str)
                else None
            ),
        )
