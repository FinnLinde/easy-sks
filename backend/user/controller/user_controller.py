"""FastAPI router for user/account endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.auth_dependencies import get_current_user, require_role
from user.model.app_user import AppUser

router = APIRouter(tags=["User"], dependencies=[require_role(Role.FREEMIUM)])


class MeOut(BaseModel):
    user_id: str
    email: Optional[str] = None
    roles: list[str]
    plan: str
    entitlements: list[str]
    billing_status: Optional[str] = None
    renews_at: Optional[str] = None
    cancels_at: Optional[str] = None


def get_current_app_user() -> AppUser:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


@router.get("/me", response_model=MeOut)
async def get_me(
    app_user: AppUser = Depends(get_current_app_user),
    auth_user: AuthenticatedUser = Depends(get_current_user),
) -> MeOut:
    roles = [r.value for r in auth_user.roles]
    plan = "premium" if auth_user.has_role(Role.PREMIUM) else "freemium"

    entitlements = ["study_access"]
    if plan == "premium":
        entitlements.append("premium_access")

    return MeOut(
        user_id=app_user.id,
        email=app_user.email,
        roles=roles,
        plan=plan,
        entitlements=entitlements,
        billing_status=None,
        renews_at=None,
        cancels_at=None,
    )
