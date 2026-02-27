"""Integration tests for user/account API endpoints."""

from __future__ import annotations

import pytest

from user.db.user_table import UserRow


@pytest.mark.asyncio
class TestMeEndpoint:
    async def test_provisions_local_user_on_authenticated_request(
        self, client, db_session
    ):
        resp = await client.get("/me")
        assert resp.status_code == 200

        user = await db_session.get(UserRow, "test-user")
        assert user is not None
        assert user.auth_provider == "cognito"
        assert user.auth_provider_user_id == "test-user"

    async def test_returns_session_identity_and_plan(self, client):
        resp = await client.get("/me")
        assert resp.status_code == 200
        data = resp.json()

        assert data["user_id"] == "test-user"
        assert data["email"] is None
        assert data["roles"] == ["freemium"]
        assert data["plan"] == "freemium"
        assert data["entitlements"] == ["study_access"]

