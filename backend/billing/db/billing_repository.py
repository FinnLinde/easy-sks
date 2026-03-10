"""Async PostgreSQL repository for billing state."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from billing.db.billing_db_mapper import BillingDbMapper
from billing.db.billing_tables import BillingCustomerRow, SubscriptionRow
from billing.model.billing_customer import BillingCustomer
from billing.model.subscription import Subscription


class BillingRepository:
    """Database adapter implementing billing persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_customer_by_user(
        self,
        user_id: str,
        provider: str,
    ) -> BillingCustomer | None:
        row = await self._session.get(
            BillingCustomerRow,
            {"user_id": user_id, "provider": provider},
        )
        if row is None:
            return None
        return BillingDbMapper.customer_to_domain(row)

    async def get_user_id_by_customer(
        self,
        stripe_customer_id: str,
        provider: str,
    ) -> str | None:
        stmt = select(BillingCustomerRow.user_id).where(
            BillingCustomerRow.provider == provider,
            BillingCustomerRow.stripe_customer_id == stripe_customer_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_customer(self, customer: BillingCustomer) -> BillingCustomer:
        row = await self._session.get(
            BillingCustomerRow,
            {"user_id": customer.user_id, "provider": customer.provider},
        )
        if row is None:
            row = BillingDbMapper.customer_to_row(customer)
            self._session.add(row)
        else:
            row.stripe_customer_id = customer.stripe_customer_id

        await self._session.flush()
        await self._session.refresh(row)
        return BillingDbMapper.customer_to_domain(row)

    async def get_subscription_by_user(
        self,
        user_id: str,
        provider: str,
    ) -> Subscription | None:
        row = await self._session.get(
            SubscriptionRow,
            {"user_id": user_id, "provider": provider},
        )
        if row is None:
            return None
        return BillingDbMapper.subscription_to_domain(row)

    async def upsert_subscription(self, subscription: Subscription) -> Subscription:
        existing_by_provider_id = await self._session.execute(
            select(SubscriptionRow).where(
                SubscriptionRow.provider == subscription.provider,
                SubscriptionRow.provider_subscription_id
                == subscription.provider_subscription_id,
            )
        )
        row = existing_by_provider_id.scalar_one_or_none()

        if row is None:
            row = await self._session.get(
                SubscriptionRow,
                {
                    "user_id": subscription.user_id,
                    "provider": subscription.provider,
                },
            )

        if row is None:
            row = SubscriptionRow(
                user_id=subscription.user_id,
                provider=subscription.provider,
                provider_subscription_id=subscription.provider_subscription_id,
                status=subscription.status,
                current_period_end=subscription.current_period_end,
                price_id=subscription.price_id,
                updated_at=subscription.updated_at,
            )
            self._session.add(row)
        else:
            row.provider_subscription_id = subscription.provider_subscription_id
            row.status = subscription.status
            row.current_period_end = subscription.current_period_end
            row.price_id = subscription.price_id
            row.updated_at = subscription.updated_at

        await self._session.flush()
        await self._session.refresh(row)
        return BillingDbMapper.subscription_to_domain(row)
