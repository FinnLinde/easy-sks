"""Domain model and plan policy for subscriptions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

PREMIUM_SUBSCRIPTION_STATUSES = {"active", "trialing"}


@dataclass(frozen=True)
class Subscription:
    """Current subscription snapshot for one user/provider."""

    user_id: str
    provider: str
    provider_subscription_id: str
    status: str
    current_period_end: datetime | None
    price_id: str | None
    updated_at: datetime


def resolve_plan_for_status(status: str | None) -> str:
    """Map provider status to internal plan (MVP policy)."""
    if status is None:
        return "freemium"
    return "premium" if status.lower() in PREMIUM_SUBSCRIPTION_STATUSES else "freemium"
