"""Domain model for external billing-customer mappings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BillingCustomer:
    """Maps one app user to one external billing customer ID."""

    user_id: str
    provider: str
    stripe_customer_id: str
