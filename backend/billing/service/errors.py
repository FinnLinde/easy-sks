"""Billing-domain error types."""

from __future__ import annotations


class BillingError(RuntimeError):
    """Base error for billing-domain failures."""


class BillingConfigurationError(BillingError):
    """Raised when required Stripe configuration is missing."""


class BillingCustomerNotFoundError(BillingError):
    """Raised when no billing customer exists for the current user."""


class StripeWebhookSignatureError(BillingError):
    """Raised when Stripe webhook signature verification fails."""
