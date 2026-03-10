"""Application service for Stripe billing orchestration."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from billing.model.billing_customer import BillingCustomer
from billing.model.entitlement_snapshot import EntitlementSnapshot
from billing.model.subscription import Subscription, resolve_plan_for_status
from billing.service.billing_repository_port import BillingRepositoryPort
from billing.service.errors import (
    BillingConfigurationError,
    BillingCustomerNotFoundError,
    BillingError,
    StripeWebhookSignatureError,
)
from billing.service.stripe_config import StripeConfig
from billing.service.stripe_gateway_port import StripeGatewayPort

_PROVIDER_STRIPE = "stripe"
_RENEWS_VISIBLE_STATUSES = {
    "active",
    "trialing",
    "past_due",
    "unpaid",
    "incomplete",
    "incomplete_expired",
}


class BillingService:
    """Coordinates Stripe checkout, portal, webhook, and plan sync."""

    def __init__(
        self,
        repository: BillingRepositoryPort,
        stripe_config: StripeConfig,
        stripe_gateway_factory: Callable[[], StripeGatewayPort],
    ) -> None:
        self._repository = repository
        self._stripe_config = stripe_config
        self._stripe_gateway_factory = stripe_gateway_factory
        self._stripe_gateway: StripeGatewayPort | None = None

    async def get_subscription_for_user(self, user_id: str) -> Subscription | None:
        return await self._repository.get_subscription_by_user(
            user_id=user_id,
            provider=_PROVIDER_STRIPE,
        )

    async def get_entitlement_snapshot(self, user_id: str) -> EntitlementSnapshot:
        subscription = await self.get_subscription_for_user(user_id)
        status = subscription.status if subscription else None
        plan = resolve_plan_for_status(status)

        entitlements = ["study_access"]
        if plan == "premium":
            entitlements.append("premium_access")

        renews_at = None
        cancels_at = None
        if subscription is not None:
            normalized_status = subscription.status.lower()
            if normalized_status in _RENEWS_VISIBLE_STATUSES:
                renews_at = subscription.current_period_end
            if normalized_status == "canceled":
                cancels_at = subscription.current_period_end

        return EntitlementSnapshot(
            plan=plan,
            entitlements=entitlements,
            billing_status=status,
            renews_at=renews_at,
            cancels_at=cancels_at,
        )

    async def create_checkout_session(self, user_id: str, email: str | None) -> str:
        self._stripe_config.require_checkout_settings()
        gateway = self._get_stripe_gateway()

        customer_id = await self._get_or_create_customer_id(user_id=user_id, email=email)
        session = gateway.create_checkout_session(
            customer_id=customer_id,
            price_id=self._must(self._stripe_config.price_id_premium, "STRIPE_PRICE_ID_PREMIUM"),
            success_url=self._must(
                self._stripe_config.checkout_success_url,
                "STRIPE_CHECKOUT_SUCCESS_URL",
            ),
            cancel_url=self._must(
                self._stripe_config.checkout_cancel_url,
                "STRIPE_CHECKOUT_CANCEL_URL",
            ),
            user_id=user_id,
        )

        checkout_url = self._as_optional_str(session.get("url"))
        if not checkout_url:
            raise BillingError("Stripe checkout session did not contain a redirect URL")
        return checkout_url

    async def create_customer_portal_session(self, user_id: str) -> str:
        self._stripe_config.require_portal_settings()
        gateway = self._get_stripe_gateway()

        customer = await self._repository.get_customer_by_user(
            user_id=user_id,
            provider=_PROVIDER_STRIPE,
        )
        if customer is None:
            raise BillingCustomerNotFoundError(
                "No Stripe customer found for this user"
            )

        session = gateway.create_customer_portal_session(
            customer_id=customer.stripe_customer_id,
            return_url=self._must(
                self._stripe_config.portal_return_url,
                "STRIPE_PORTAL_RETURN_URL",
            ),
        )
        portal_url = self._as_optional_str(session.get("url"))
        if not portal_url:
            raise BillingError("Stripe portal session did not contain a redirect URL")
        return portal_url

    async def process_stripe_webhook(self, payload: bytes, signature: str | None) -> str:
        self._stripe_config.require_webhook_settings()

        if not signature:
            raise StripeWebhookSignatureError("Missing Stripe signature")

        gateway = self._get_stripe_gateway()
        event = gateway.construct_webhook_event(
            payload=payload,
            signature=signature,
            webhook_secret=self._must(
                self._stripe_config.webhook_secret,
                "STRIPE_WEBHOOK_SECRET",
            ),
        )

        event_type = self._as_optional_str(event.get("type")) or "unknown"
        event_object = self._extract_event_object(event)
        if event_object is None:
            return event_type

        if event_type in {
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        }:
            await self._upsert_subscription_from_payload(event_object)
            return event_type

        if event_type == "checkout.session.completed":
            await self._handle_checkout_completed(event_object)
            return event_type

        return event_type

    async def _get_or_create_customer_id(self, user_id: str, email: str | None) -> str:
        existing = await self._repository.get_customer_by_user(
            user_id=user_id,
            provider=_PROVIDER_STRIPE,
        )
        if existing is not None:
            return existing.stripe_customer_id

        customer = self._get_stripe_gateway().create_customer(
            email=email,
            metadata={"user_id": user_id},
        )
        customer_id = self._as_optional_str(customer.get("id"))
        if not customer_id:
            raise BillingError("Stripe customer creation returned no ID")

        await self._repository.upsert_customer(
            BillingCustomer(
                user_id=user_id,
                provider=_PROVIDER_STRIPE,
                stripe_customer_id=customer_id,
            )
        )
        return customer_id

    async def _handle_checkout_completed(self, event_object: dict[str, Any]) -> None:
        if self._as_optional_str(event_object.get("mode")) != "subscription":
            return

        stripe_customer_id = self._as_optional_str(event_object.get("customer"))
        subscription_id = self._as_optional_str(event_object.get("subscription"))
        user_id = self._extract_user_id(event_object)

        if stripe_customer_id and user_id:
            await self._repository.upsert_customer(
                BillingCustomer(
                    user_id=user_id,
                    provider=_PROVIDER_STRIPE,
                    stripe_customer_id=stripe_customer_id,
                )
            )

        if not user_id and stripe_customer_id:
            user_id = await self._repository.get_user_id_by_customer(
                stripe_customer_id=stripe_customer_id,
                provider=_PROVIDER_STRIPE,
            )

        if not subscription_id or not user_id:
            return

        subscription_payload = self._get_stripe_gateway().retrieve_subscription(
            subscription_id
        )
        await self._upsert_subscription_from_payload(
            subscription_payload,
            fallback_user_id=user_id,
        )

    async def _upsert_subscription_from_payload(
        self,
        payload: dict[str, Any],
        fallback_user_id: str | None = None,
    ) -> None:
        provider_subscription_id = self._as_optional_str(payload.get("id"))
        status = self._as_optional_str(payload.get("status"))
        stripe_customer_id = self._as_optional_str(payload.get("customer"))
        current_period_end = self._parse_unix_timestamp(payload.get("current_period_end"))
        price_id = self._extract_price_id(payload)

        metadata = payload.get("metadata")
        metadata_user_id = None
        if isinstance(metadata, dict):
            metadata_user_id = self._as_optional_str(metadata.get("user_id"))

        user_id = metadata_user_id or fallback_user_id
        if user_id is None and stripe_customer_id is not None:
            user_id = await self._repository.get_user_id_by_customer(
                stripe_customer_id=stripe_customer_id,
                provider=_PROVIDER_STRIPE,
            )

        if (
            provider_subscription_id is None
            or status is None
            or user_id is None
        ):
            return

        if stripe_customer_id:
            await self._repository.upsert_customer(
                BillingCustomer(
                    user_id=user_id,
                    provider=_PROVIDER_STRIPE,
                    stripe_customer_id=stripe_customer_id,
                )
            )

        await self._repository.upsert_subscription(
            Subscription(
                user_id=user_id,
                provider=_PROVIDER_STRIPE,
                provider_subscription_id=provider_subscription_id,
                status=status,
                current_period_end=current_period_end,
                price_id=price_id,
                updated_at=datetime.now(timezone.utc),
            )
        )

    def _get_stripe_gateway(self) -> StripeGatewayPort:
        if self._stripe_gateway is None:
            self._stripe_gateway = self._stripe_gateway_factory()
        return self._stripe_gateway

    @staticmethod
    def _extract_event_object(event: dict[str, Any]) -> dict[str, Any] | None:
        data = event.get("data")
        if not isinstance(data, dict):
            return None
        event_object = data.get("object")
        if not isinstance(event_object, dict):
            return None
        return event_object

    @staticmethod
    def _extract_user_id(payload: dict[str, Any]) -> str | None:
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            user_id = BillingService._as_optional_str(metadata.get("user_id"))
            if user_id:
                return user_id

        return BillingService._as_optional_str(payload.get("client_reference_id"))

    @staticmethod
    def _extract_price_id(payload: dict[str, Any]) -> str | None:
        items = payload.get("items")
        if not isinstance(items, dict):
            return None

        data_items = items.get("data")
        if not isinstance(data_items, list) or not data_items:
            return None

        first_item = data_items[0]
        if not isinstance(first_item, dict):
            return None

        price = first_item.get("price")
        if not isinstance(price, dict):
            return None

        return BillingService._as_optional_str(price.get("id"))

    @staticmethod
    def _parse_unix_timestamp(value: Any) -> datetime | None:
        if isinstance(value, int | float):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return None

    @staticmethod
    def _as_optional_str(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return str(value)

    @staticmethod
    def _must(value: str | None, env_name: str) -> str:
        if not value:
            raise BillingConfigurationError(f"Missing required setting {env_name}")
        return value
