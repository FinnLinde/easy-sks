"""FastAPI router for user/account endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth.model.authenticated_user import AuthenticatedUser
from auth.model.role import Role
from auth.service.auth_dependencies import get_current_user, require_role
from billing.service.billing_service import BillingService
from user.model.app_user import AppUser
from user.model.profile_validation import ProfileValidationError
from user.service.user_profile_service import MobileNumberInUseError, UserProfileService

router = APIRouter(tags=["User"], dependencies=[require_role(Role.FREEMIUM)])


class MeOut(BaseModel):
    user_id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    profile_complete: bool
    roles: list[str]
    plan: str
    entitlements: list[str]
    billing_status: Optional[str] = None
    renews_at: Optional[str] = None
    cancels_at: Optional[str] = None


class ProfileUpdateIn(BaseModel):
    full_name: str
    mobile_number: str


def get_current_app_user() -> AppUser:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


def get_user_profile_service() -> UserProfileService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


def get_billing_service() -> BillingService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


async def _build_me_out(
    app_user: AppUser,
    auth_user: AuthenticatedUser,
    billing_service: BillingService,
) -> MeOut:
    roles = [r.value for r in auth_user.roles]
    snapshot = await billing_service.get_entitlement_snapshot(app_user.id)

    return MeOut(
        user_id=app_user.id,
        email=app_user.email,
        full_name=app_user.full_name,
        mobile_number=app_user.mobile_number,
        profile_complete=app_user.profile_complete,
        roles=roles,
        plan=snapshot.plan,
        entitlements=snapshot.entitlements,
        billing_status=snapshot.billing_status,
        renews_at=snapshot.renews_at.isoformat() if snapshot.renews_at else None,
        cancels_at=snapshot.cancels_at.isoformat() if snapshot.cancels_at else None,
    )


@router.get("/me", response_model=MeOut)
async def get_me(
    app_user: AppUser = Depends(get_current_app_user),
    auth_user: AuthenticatedUser = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
) -> MeOut:
    return await _build_me_out(
        app_user=app_user,
        auth_user=auth_user,
        billing_service=billing_service,
    )


@router.patch(
    "/me/profile",
    response_model=MeOut,
    responses={status.HTTP_400_BAD_REQUEST: {}, status.HTTP_409_CONFLICT: {}},
)
async def patch_me_profile(
    body: ProfileUpdateIn,
    app_user: AppUser = Depends(get_current_app_user),
    auth_user: AuthenticatedUser = Depends(get_current_user),
    profile_service: UserProfileService = Depends(get_user_profile_service),
    billing_service: BillingService = Depends(get_billing_service),
) -> MeOut:
    try:
        updated_user = await profile_service.update_profile(
            user_id=app_user.id,
            full_name=body.full_name,
            mobile_number=body.mobile_number,
        )
    except ProfileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.code,
        )
    except MobileNumberInUseError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="mobile_number_in_use",
        )

    return await _build_me_out(
        app_user=updated_user,
        auth_user=auth_user,
        billing_service=billing_service,
    )
