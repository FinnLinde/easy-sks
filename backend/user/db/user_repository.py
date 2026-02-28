"""Async PostgreSQL implementation for local users."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from user.db.user_table import UserRow
from user.model.app_user import AppUser


class UserNotFoundError(LookupError):
    """Raised when the target user does not exist."""


class MobileNumberConflictError(ValueError):
    """Raised when a mobile number already belongs to another user."""


class UserRepository:
    """CRUD/upsert access for local app users."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(row: UserRow) -> AppUser:
        return AppUser(
            id=row.id,
            auth_provider=row.auth_provider,
            auth_provider_user_id=row.auth_provider_user_id,
            email=row.email,
            full_name=row.full_name,
            mobile_number=row.mobile_number,
            mobile_verified_at=row.mobile_verified_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _is_mobile_number_conflict(exc: IntegrityError) -> bool:
        constraint_name = getattr(exc.orig, "constraint_name", None)
        if constraint_name == "uq_users_mobile_number":
            return True
        return "uq_users_mobile_number" in str(exc.orig)

    async def get_by_id(self, user_id: str) -> AppUser | None:
        row = await self._session.get(UserRow, user_id)
        if row is None:
            return None
        return self._to_domain(row)

    async def get_by_auth_provider_user_id(
        self, auth_provider: str, auth_provider_user_id: str
    ) -> AppUser | None:
        stmt = select(UserRow).where(
            UserRow.auth_provider == auth_provider,
            UserRow.auth_provider_user_id == auth_provider_user_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    async def get_or_create_cognito_user(
        self, cognito_sub: str, email: str | None
    ) -> AppUser:
        existing = await self.get_by_auth_provider_user_id("cognito", cognito_sub)
        if existing is not None:
            # Keep email in sync when Cognito token starts/stops providing it.
            if existing.email != email:
                row = await self._session.get(UserRow, existing.id)
                if row is not None:
                    row.email = email
                    await self._session.flush()
                    await self._session.refresh(row)
                    return self._to_domain(row)
            return existing

        row = UserRow(
            id=cognito_sub,
            auth_provider="cognito",
            auth_provider_user_id=cognito_sub,
            email=email,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return self._to_domain(row)

    async def update_profile(
        self, user_id: str, full_name: str, mobile_number: str
    ) -> AppUser:
        """Persist full name and mobile number for a local user."""
        row = await self._session.get(UserRow, user_id)
        if row is None:
            raise UserNotFoundError(f"User {user_id!r} not found")

        previous_mobile_number = row.mobile_number
        row.full_name = full_name
        row.mobile_number = mobile_number
        if previous_mobile_number != mobile_number:
            row.mobile_verified_at = None

        try:
            await self._session.flush()
        except IntegrityError as exc:
            if self._is_mobile_number_conflict(exc):
                raise MobileNumberConflictError("mobile_number_in_use") from exc
            raise

        await self._session.refresh(row)
        return self._to_domain(row)
