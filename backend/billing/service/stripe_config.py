"""Environment-backed Stripe configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings

from billing.service.errors import BillingConfigurationError


class StripeConfig(BaseSettings):
    """Settings used by checkout, portal, and webhook handlers."""

    secret_key: str | None = None
    webhook_secret: str | None = None
    price_id_premium: str | None = None
    checkout_success_url: str | None = None
    checkout_cancel_url: str | None = None
    portal_return_url: str | None = None

    model_config = {"env_prefix": "STRIPE_"}

    def require_checkout_settings(self) -> None:
        missing = []
        if not self.secret_key:
            missing.append("STRIPE_SECRET_KEY")
        if not self.price_id_premium:
            missing.append("STRIPE_PRICE_ID_PREMIUM")
        if not self.checkout_success_url:
            missing.append("STRIPE_CHECKOUT_SUCCESS_URL")
        if not self.checkout_cancel_url:
            missing.append("STRIPE_CHECKOUT_CANCEL_URL")
        if missing:
            raise BillingConfigurationError(
                f"Missing Stripe checkout config: {', '.join(missing)}"
            )

    def require_portal_settings(self) -> None:
        missing = []
        if not self.secret_key:
            missing.append("STRIPE_SECRET_KEY")
        if not self.portal_return_url:
            missing.append("STRIPE_PORTAL_RETURN_URL")
        if missing:
            raise BillingConfigurationError(
                f"Missing Stripe portal config: {', '.join(missing)}"
            )

    def require_webhook_settings(self) -> None:
        missing = []
        if not self.secret_key:
            missing.append("STRIPE_SECRET_KEY")
        if not self.webhook_secret:
            missing.append("STRIPE_WEBHOOK_SECRET")
        if missing:
            raise BillingConfigurationError(
                f"Missing Stripe webhook config: {', '.join(missing)}"
            )
