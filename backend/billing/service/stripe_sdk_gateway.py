"""Stripe SDK adapter implementation."""

from __future__ import annotations

import importlib
from typing import Any

from billing.service.errors import BillingConfigurationError, StripeWebhookSignatureError
from billing.service.stripe_gateway_port import StripeGatewayPort


class StripeSdkGateway(StripeGatewayPort):
    """Gateway that delegates billing operations to the official Stripe SDK."""

    def __init__(self, api_key: str | None) -> None:
        if not api_key:
            raise BillingConfigurationError("Missing Stripe API key")

        try:
            stripe_module = importlib.import_module("stripe")
        except ModuleNotFoundError as exc:
            raise BillingConfigurationError(
                "Stripe SDK is not installed. Add 'stripe' to backend dependencies."
            ) from exc

        stripe_module.api_key = api_key
        self._stripe = stripe_module

    def create_customer(
        self,
        *,
        email: str | None,
        metadata: dict[str, str],
    ) -> dict[str, Any]:
        customer = self._stripe.Customer.create(email=email, metadata=metadata)
        return self._to_dict(customer)

    def create_checkout_session(
        self,
        *,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: str,
    ) -> dict[str, Any]:
        session = self._stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=user_id,
            metadata={"user_id": user_id},
            subscription_data={"metadata": {"user_id": user_id}},
        )
        return self._to_dict(session)

    def create_customer_portal_session(
        self,
        *,
        customer_id: str,
        return_url: str,
    ) -> dict[str, Any]:
        session = self._stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return self._to_dict(session)

    def construct_webhook_event(
        self,
        *,
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ) -> dict[str, Any]:
        try:
            event = self._stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=webhook_secret,
            )
        except Exception as exc:  # pragma: no cover - SDK-specific branches
            signature_error_cls = getattr(
                getattr(self._stripe, "error", object),
                "SignatureVerificationError",
                None,
            )
            if signature_error_cls and isinstance(exc, signature_error_cls):
                raise StripeWebhookSignatureError("invalid_stripe_signature") from exc
            raise

        return self._to_dict(event)

    def retrieve_subscription(self, subscription_id: str) -> dict[str, Any]:
        subscription = self._stripe.Subscription.retrieve(
            subscription_id,
            expand=["items.data.price"],
        )
        return self._to_dict(subscription)

    @staticmethod
    def _to_dict(value: Any) -> dict[str, Any]:
        if hasattr(value, "to_dict_recursive"):
            return value.to_dict_recursive()
        if isinstance(value, dict):
            return value
        return dict(value)
