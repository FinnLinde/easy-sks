"""Abstraction over Stripe SDK calls."""

from __future__ import annotations

from typing import Any, Protocol


class StripeGatewayPort(Protocol):
    """Operations the billing service needs from Stripe."""

    def create_customer(
        self,
        *,
        email: str | None,
        metadata: dict[str, str],
    ) -> dict[str, Any]: ...

    def create_checkout_session(
        self,
        *,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: str,
    ) -> dict[str, Any]: ...

    def create_customer_portal_session(
        self,
        *,
        customer_id: str,
        return_url: str,
    ) -> dict[str, Any]: ...

    def construct_webhook_event(
        self,
        *,
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ) -> dict[str, Any]: ...

    def retrieve_subscription(self, subscription_id: str) -> dict[str, Any]: ...
