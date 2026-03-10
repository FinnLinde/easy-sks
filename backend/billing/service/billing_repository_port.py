"""Repository abstraction for billing persistence operations."""

from __future__ import annotations

from typing import Protocol

from billing.model.billing_customer import BillingCustomer
from billing.model.subscription import Subscription


class BillingRepositoryPort(Protocol):
    """Persistence operations required by the billing service."""

    async def get_customer_by_user(
        self,
        user_id: str,
        provider: str,
    ) -> BillingCustomer | None: ...

    async def get_user_id_by_customer(
        self,
        stripe_customer_id: str,
        provider: str,
    ) -> str | None: ...

    async def upsert_customer(self, customer: BillingCustomer) -> BillingCustomer: ...

    async def get_subscription_by_user(
        self,
        user_id: str,
        provider: str,
    ) -> Subscription | None: ...

    async def upsert_subscription(self, subscription: Subscription) -> Subscription: ...
