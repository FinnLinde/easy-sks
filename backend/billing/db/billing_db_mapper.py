"""Mapping between billing ORM rows and domain objects."""

from __future__ import annotations

from billing.db.billing_tables import BillingCustomerRow, SubscriptionRow
from billing.model.billing_customer import BillingCustomer
from billing.model.subscription import Subscription


class BillingDbMapper:
    """Translate DB rows to domain models and back."""

    @staticmethod
    def customer_to_domain(row: BillingCustomerRow) -> BillingCustomer:
        return BillingCustomer(
            user_id=row.user_id,
            provider=row.provider,
            stripe_customer_id=row.stripe_customer_id,
        )

    @staticmethod
    def customer_to_row(customer: BillingCustomer) -> BillingCustomerRow:
        return BillingCustomerRow(
            user_id=customer.user_id,
            provider=customer.provider,
            stripe_customer_id=customer.stripe_customer_id,
        )

    @staticmethod
    def subscription_to_domain(row: SubscriptionRow) -> Subscription:
        return Subscription(
            user_id=row.user_id,
            provider=row.provider,
            provider_subscription_id=row.provider_subscription_id,
            status=row.status,
            current_period_end=row.current_period_end,
            price_id=row.price_id,
            updated_at=row.updated_at,
        )
