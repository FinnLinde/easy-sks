"""Integration tests for billing endpoints and webhook syncing."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from billing.controller.billing_controller import get_billing_service
from billing.db.billing_repository import BillingRepository
from billing.db.billing_tables import BillingCustomerRow, SubscriptionRow
from billing.service.billing_service import BillingService
from billing.service.errors import BillingCustomerNotFoundError, StripeWebhookSignatureError
from billing.service.stripe_config import StripeConfig
from main import app
from user.db.user_table import UserRow


async def _add_user(db_session, user_id: str) -> None:
    db_session.add(
        UserRow(
            id=user_id,
            auth_provider="cognito",
            auth_provider_user_id=user_id,
            email=f"{user_id}@example.com",
        )
    )
    await db_session.flush()


class _FakeBillingService:
    def __init__(self) -> None:
        self.checkout_calls: list[tuple[str, str | None]] = []
        self.portal_calls: list[str] = []
        self.raise_portal_not_found = False
        self.raise_invalid_signature = False

    async def create_checkout_session(self, user_id: str, email: str | None) -> str:
        self.checkout_calls.append((user_id, email))
        return "https://checkout.stripe.test/session"

    async def create_customer_portal_session(self, user_id: str) -> str:
        self.portal_calls.append(user_id)
        if self.raise_portal_not_found:
            raise BillingCustomerNotFoundError("No Stripe customer found for this user")
        return "https://billing.stripe.test/portal"

    async def process_stripe_webhook(self, payload: bytes, signature: str | None) -> str:
        if self.raise_invalid_signature:
            raise StripeWebhookSignatureError("invalid_stripe_signature")
        return "customer.subscription.updated"

    async def get_subscription_for_user(self, user_id: str):  # pragma: no cover - not used
        return None


class _FakeStripeGateway:
    def create_customer(self, *, email: str | None, metadata: dict[str, str]):
        return {"id": "cus_created"}

    def create_checkout_session(
        self,
        *,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: str,
    ):
        return {"id": "cs_test", "url": "https://checkout.stripe.test/session"}

    def create_customer_portal_session(self, *, customer_id: str, return_url: str):
        return {"id": "bps_test", "url": "https://billing.stripe.test/portal"}

    def construct_webhook_event(
        self,
        *,
        payload: bytes,
        signature: str,
        webhook_secret: str,
    ):
        if signature != "valid-signature":
            raise StripeWebhookSignatureError("invalid_stripe_signature")

        return {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_123",
                    "customer": "cus_123",
                    "status": "active",
                    "current_period_end": 1760000000,
                    "metadata": {"user_id": "test-user"},
                    "items": {"data": [{"price": {"id": "price_premium"}}]},
                }
            },
        }

    def retrieve_subscription(self, subscription_id: str):
        return {
            "id": subscription_id,
            "customer": "cus_123",
            "status": "active",
            "current_period_end": 1760000000,
            "metadata": {"user_id": "test-user"},
            "items": {"data": [{"price": {"id": "price_premium"}}]},
        }


@pytest.mark.asyncio
class TestBillingApi:
    async def test_checkout_and_portal_return_urls(self, client):
        fake = _FakeBillingService()
        original_override = app.dependency_overrides.get(get_billing_service)
        app.dependency_overrides[get_billing_service] = lambda: fake
        try:
            checkout = await client.post("/billing/checkout-session")
            assert checkout.status_code == 200
            assert checkout.json()["checkout_url"] == "https://checkout.stripe.test/session"

            portal = await client.post("/billing/customer-portal-session")
            assert portal.status_code == 200
            assert portal.json()["portal_url"] == "https://billing.stripe.test/portal"

            assert fake.checkout_calls == [("test-user", None)]
            assert fake.portal_calls == ["test-user"]
        finally:
            if original_override is None:
                app.dependency_overrides.pop(get_billing_service, None)
            else:
                app.dependency_overrides[get_billing_service] = original_override

    async def test_portal_returns_404_when_customer_missing(self, client):
        fake = _FakeBillingService()
        fake.raise_portal_not_found = True
        original_override = app.dependency_overrides.get(get_billing_service)
        app.dependency_overrides[get_billing_service] = lambda: fake
        try:
            response = await client.post("/billing/customer-portal-session")
            assert response.status_code == 404
            assert response.json()["detail"] == "No Stripe customer found for this user"
        finally:
            if original_override is None:
                app.dependency_overrides.pop(get_billing_service, None)
            else:
                app.dependency_overrides[get_billing_service] = original_override

    async def test_webhook_signature_error_returns_400(self, client):
        fake = _FakeBillingService()
        fake.raise_invalid_signature = True
        original_override = app.dependency_overrides.get(get_billing_service)
        app.dependency_overrides[get_billing_service] = lambda: fake
        try:
            response = await client.post(
                "/billing/webhook/stripe",
                content='{"id":"evt_1"}',
                headers={"stripe-signature": "bad-signature"},
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "invalid_stripe_signature"
        finally:
            if original_override is None:
                app.dependency_overrides.pop(get_billing_service, None)
            else:
                app.dependency_overrides[get_billing_service] = original_override

    async def test_webhook_is_idempotent_for_repeated_events(self, client, db_session):
        await _add_user(db_session, "test-user")

        service = BillingService(
            repository=BillingRepository(db_session),
            stripe_config=StripeConfig(
                secret_key="sk_test_123",
                webhook_secret="whsec_123",
                price_id_premium="price_premium",
                checkout_success_url="http://localhost:3000/account?success=true",
                checkout_cancel_url="http://localhost:3000/account?canceled=true",
                portal_return_url="http://localhost:3000/account",
            ),
            stripe_gateway_factory=lambda: _FakeStripeGateway(),
        )

        original_override = app.dependency_overrides.get(get_billing_service)
        app.dependency_overrides[get_billing_service] = lambda: service
        try:
            first = await client.post(
                "/billing/webhook/stripe",
                content='{"id":"evt_1"}',
                headers={"stripe-signature": "valid-signature"},
            )
            second = await client.post(
                "/billing/webhook/stripe",
                content='{"id":"evt_1"}',
                headers={"stripe-signature": "valid-signature"},
            )

            assert first.status_code == 200
            assert second.status_code == 200

            subscription_count = await db_session.execute(
                select(func.count())
                .select_from(SubscriptionRow)
                .where(
                    SubscriptionRow.user_id == "test-user",
                    SubscriptionRow.provider == "stripe",
                )
            )
            assert subscription_count.scalar_one() == 1

            customer_count = await db_session.execute(
                select(func.count())
                .select_from(BillingCustomerRow)
                .where(
                    BillingCustomerRow.user_id == "test-user",
                    BillingCustomerRow.provider == "stripe",
                )
            )
            assert customer_count.scalar_one() == 1

            subscription_row = (
                await db_session.execute(
                    select(SubscriptionRow).where(
                        SubscriptionRow.user_id == "test-user",
                        SubscriptionRow.provider == "stripe",
                    )
                )
            ).scalar_one()
            assert subscription_row.status == "active"
            assert subscription_row.provider_subscription_id == "sub_123"
            assert subscription_row.price_id == "price_premium"
            assert subscription_row.current_period_end == datetime.fromtimestamp(
                1760000000,
                tz=timezone.utc,
            )
        finally:
            if original_override is None:
                app.dependency_overrides.pop(get_billing_service, None)
            else:
                app.dependency_overrides[get_billing_service] = original_override

    async def test_subscription_endpoint_returns_freemium_without_subscription(self, client):
        response = await client.get("/billing/subscription")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "stripe"
        assert data["status"] is None
        assert data["plan"] == "freemium"


@pytest.mark.asyncio
async def test_checkout_requires_authentication() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as unauth_client:
        response = await unauth_client.post("/billing/checkout-session")

    assert response.status_code in {401, 403}
