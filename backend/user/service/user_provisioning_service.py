"""Provision local app users from authenticated principals."""

from __future__ import annotations

from auth.model.authenticated_user import AuthenticatedUser
from user.db.user_repository import UserRepository
from user.model.app_user import AppUser


class UserProvisioningService:
    """Ensures a local app user exists for an authenticated principal."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def get_or_create_for_authenticated_user(
        self, auth_user: AuthenticatedUser
    ) -> AppUser:
        return await self._user_repository.get_or_create_cognito_user(
            cognito_sub=auth_user.user_id,
            email=auth_user.email,
        )
