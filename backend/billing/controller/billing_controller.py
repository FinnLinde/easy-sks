"""FastAPI router for billing and Stripe webhook endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from auth.model.role import Role
from auth.service.auth_dependencies import require_role
from billing.model.subscription import resolve_plan_for_status
from billing.service.billing_service import BillingService
from billing.service.errors import (
    BillingConfigurationError,
    BillingCustomerNotFoundError,
    StripeWebhookSignatureError,
)
from user.model.app_user import AppUser

router = APIRouter(tags=["Billing"])


class CheckoutSessionOut(BaseModel):
    checkout_url: str


class CustomerPortalSessionOut(BaseModel):
    portal_url: str


class SubscriptionOut(BaseModel):
    provider: str
    status: Optional[str] = None
    plan: str
    current_period_end: Optional[str] = None
    price_id: Optional[str] = None


class StripeWebhookReceiptOut(BaseModel):
    received: bool
    event_type: str


def get_billing_service() -> BillingService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


def get_current_app_user() -> AppUser:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


@router.post(
    "/billing/checkout-session",
    response_model=CheckoutSessionOut,
    dependencies=[require_role(Role.FREEMIUM)],
)
async def create_checkout_session(
    billing_service: BillingService = Depends(get_billing_service),
    user: AppUser = Depends(get_current_app_user),
) -> CheckoutSessionOut:
    try:
        checkout_url = await billing_service.create_checkout_session(
            user_id=user.id,
            email=user.email,
        )
    except BillingConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    return CheckoutSessionOut(checkout_url=checkout_url)


@router.post(
    "/billing/customer-portal-session",
    response_model=CustomerPortalSessionOut,
    dependencies=[require_role(Role.FREEMIUM)],
)
async def create_customer_portal_session(
    billing_service: BillingService = Depends(get_billing_service),
    user: AppUser = Depends(get_current_app_user),
) -> CustomerPortalSessionOut:
    try:
        portal_url = await billing_service.create_customer_portal_session(user_id=user.id)
    except BillingCustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BillingConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    return CustomerPortalSessionOut(portal_url=portal_url)


@router.post(
    "/billing/webhook/stripe",
    response_model=StripeWebhookReceiptOut,
)
async def stripe_webhook(
    request: Request,
    billing_service: BillingService = Depends(get_billing_service),
) -> StripeWebhookReceiptOut:
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    try:
        event_type = await billing_service.process_stripe_webhook(
            payload=payload,
            signature=signature,
        )
    except StripeWebhookSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except BillingConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    return StripeWebhookReceiptOut(received=True, event_type=event_type)


@router.get(
    "/billing/subscription",
    response_model=SubscriptionOut,
    dependencies=[require_role(Role.FREEMIUM)],
)
async def get_subscription(
    billing_service: BillingService = Depends(get_billing_service),
    user: AppUser = Depends(get_current_app_user),
) -> SubscriptionOut:
    subscription = await billing_service.get_subscription_for_user(user_id=user.id)
    if subscription is None:
        return SubscriptionOut(
            provider="stripe",
            status=None,
            plan="freemium",
            current_period_end=None,
            price_id=None,
        )

    return SubscriptionOut(
        provider=subscription.provider,
        status=subscription.status,
        plan=resolve_plan_for_status(subscription.status),
        current_period_end=(
            subscription.current_period_end.isoformat()
            if subscription.current_period_end
            else None
        ),
        price_id=subscription.price_id,
    )
