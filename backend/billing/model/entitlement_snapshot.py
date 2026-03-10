"""Computed entitlement surface for account responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EntitlementSnapshot:
    """Plan + billing state shown to the frontend."""

    plan: str
    entitlements: list[str]
    billing_status: str | None
    renews_at: datetime | None
    cancels_at: datetime | None
