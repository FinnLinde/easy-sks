"""Unit tests for CognitoTokenVerifier (JWKS interaction is mocked)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jwt.exceptions import InvalidTokenError

from auth.model.role import Role
from auth.service.auth_config import AuthConfig
from auth.service.cognito_token_verifier import CognitoTokenVerifier


# -- Helpers ----------------------------------------------------------------

def _generate_rsa_keypair():
    """Generate a fresh RSA private/public key pair for testing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )
    return private_key


def _encode_cognito_token(
    private_key,
    user_id: str = "cognito-user",
    groups: list[str] | None = None,
    issuer: str = "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_TestPool",
    audience: str = "test-client-id",
    expired: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (timedelta(seconds=-1) if expired else timedelta(hours=1))
    payload: dict[str, object] = {
        "sub": user_id,
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "exp": exp,
    }
    if groups is not None:
        payload["cognito:groups"] = groups

    return pyjwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )


# -- Fixtures ---------------------------------------------------------------


@pytest.fixture
def rsa_key():
    return _generate_rsa_keypair()


@pytest.fixture
def config() -> AuthConfig:
    return AuthConfig(
        cognito_user_pool_id="eu-central-1_TestPool",
        cognito_region="eu-central-1",
        cognito_app_client_id="test-client-id",
    )


@pytest.fixture
def verifier(config: AuthConfig, rsa_key) -> CognitoTokenVerifier:
    """Build a CognitoTokenVerifier with a mocked PyJWKClient."""
    with patch(
        "auth.service.cognito_token_verifier.PyJWKClient"
    ) as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        mock_signing_key = MagicMock()
        mock_signing_key.key = rsa_key.public_key()
        mock_client.get_signing_key_from_jwt.return_value = mock_signing_key

        verifier = CognitoTokenVerifier(config)
    # Replace the internal client with our mock so verify_token uses it
    verifier._jwk_client = mock_client
    return verifier


# -- Tests ------------------------------------------------------------------


class TestCognitoVerifyToken:
    def test_valid_token_with_groups(
        self, verifier: CognitoTokenVerifier, rsa_key
    ) -> None:
        token = _encode_cognito_token(
            rsa_key, user_id="abc-123", groups=["freemium", "premium"]
        )
        user = verifier.verify_token(token)

        assert user.user_id == "abc-123"
        assert user.roles == [Role.FREEMIUM, Role.PREMIUM]

    def test_valid_token_without_groups(
        self, verifier: CognitoTokenVerifier, rsa_key
    ) -> None:
        token = _encode_cognito_token(rsa_key, user_id="abc-456")
        user = verifier.verify_token(token)

        assert user.user_id == "abc-456"
        assert user.roles == []

    def test_unknown_groups_are_ignored(
        self, verifier: CognitoTokenVerifier, rsa_key
    ) -> None:
        token = _encode_cognito_token(
            rsa_key, groups=["admin", "some-other-group"]
        )
        user = verifier.verify_token(token)
        assert user.roles == [Role.ADMIN]

    def test_expired_token_raises(
        self, verifier: CognitoTokenVerifier, rsa_key
    ) -> None:
        token = _encode_cognito_token(rsa_key, expired=True)
        with pytest.raises(InvalidTokenError):
            verifier.verify_token(token)

    def test_wrong_issuer_raises(
        self, verifier: CognitoTokenVerifier, rsa_key
    ) -> None:
        token = _encode_cognito_token(
            rsa_key, issuer="https://evil.example.com"
        )
        with pytest.raises(InvalidTokenError):
            verifier.verify_token(token)


class TestCognitoConfigValidation:
    def test_missing_pool_id_raises(self) -> None:
        config = AuthConfig(
            cognito_region="eu-central-1",
        )
        with pytest.raises(ValueError, match="cognito_user_pool_id"):
            CognitoTokenVerifier(config)

    def test_missing_region_raises(self) -> None:
        config = AuthConfig(
            cognito_user_pool_id="eu-central-1_Pool",
        )
        with pytest.raises(ValueError, match="cognito_region"):
            CognitoTokenVerifier(config)
