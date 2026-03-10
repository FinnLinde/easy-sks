"""SQLAlchemy ORM models for billing persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class BillingCustomerRow(Base):
    """Maps app users to provider customer identifiers."""

    __tablename__ = "billing_customers"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "stripe_customer_id",
            name="uq_billing_customers_provider_customer",
        ),
        Index("ix_billing_customers_user_id", "user_id"),
        Index(
            "ix_billing_customers_provider_customer",
            "provider",
            "stripe_customer_id",
        ),
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id"),
        primary_key=True,
    )
    provider: Mapped[str] = mapped_column(String(32), primary_key=True)
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=False)


class SubscriptionRow(Base):
    """Persistent subscription state per user/provider."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_subscription_id",
            name="uq_subscriptions_provider_subscription",
        ),
        Index("ix_subscriptions_user_id", "user_id"),
        Index(
            "ix_subscriptions_provider_subscription_id",
            "provider",
            "provider_subscription_id",
        ),
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id"),
        primary_key=True,
    )
    provider: Mapped[str] = mapped_column(String(32), primary_key=True)
    provider_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
