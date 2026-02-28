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
        assert data["full_name"] is None
        assert data["mobile_number"] is None
        assert data["profile_complete"] is False
        assert data["roles"] == ["freemium"]
        assert data["plan"] == "freemium"
        assert data["entitlements"] == ["study_access"]
        assert data["billing_status"] is None
        assert data["renews_at"] is None
        assert data["cancels_at"] is None


@pytest.mark.asyncio
class TestPatchMeProfileEndpoint:
    async def test_updates_profile_fields(self, client, db_session):
        resp = await client.patch(
            "/me/profile",
            json={
                "full_name": "  Max   Mustermann  ",
                "mobile_number": "+491701234567",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Max Mustermann"
        assert data["mobile_number"] == "+491701234567"
        assert data["profile_complete"] is True

        user = await db_session.get(UserRow, "test-user")
        assert user is not None
        assert user.full_name == "Max Mustermann"
        assert user.mobile_number == "+491701234567"

    async def test_rejects_invalid_full_name(self, client):
        resp = await client.patch(
            "/me/profile",
            json={"full_name": " ", "mobile_number": "+491701234567"},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "invalid_full_name"

    async def test_rejects_invalid_mobile_number(self, client):
        resp = await client.patch(
            "/me/profile",
            json={"full_name": "Max Mustermann", "mobile_number": "01701234567"},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "invalid_mobile_number"

    async def test_returns_conflict_for_duplicate_mobile_number(
        self, client, db_session
    ):
        db_session.add(
            UserRow(
                id="other-user",
                auth_provider="cognito",
                auth_provider_user_id="other-user",
                email="other@example.com",
                full_name="Other User",
                mobile_number="+491701112223",
            )
        )
        await db_session.flush()

        resp = await client.patch(
            "/me/profile",
            json={
                "full_name": "Max Mustermann",
                "mobile_number": "+491701112223",
            },
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "mobile_number_in_use"
