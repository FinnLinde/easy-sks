"""add billing customers and subscriptions tables

Revision ID: 5a3d6a1e2f44
Revises: e6b4c1d9f7a2
Create Date: 2026-03-03 22:05:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a3d6a1e2f44"
down_revision: Union[str, None] = "e6b4c1d9f7a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_customers",
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "provider"),
        sa.UniqueConstraint(
            "provider",
            "stripe_customer_id",
            name="uq_billing_customers_provider_customer",
        ),
    )
    op.create_index("ix_billing_customers_user_id", "billing_customers", ["user_id"])
    op.create_index(
        "ix_billing_customers_provider_customer",
        "billing_customers",
        ["provider", "stripe_customer_id"],
    )

    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_subscription_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_id", sa.String(length=255), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "provider"),
        sa.UniqueConstraint(
            "provider",
            "provider_subscription_id",
            name="uq_subscriptions_provider_subscription",
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index(
        "ix_subscriptions_provider_subscription_id",
        "subscriptions",
        ["provider", "provider_subscription_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_subscriptions_provider_subscription_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index(
        "ix_billing_customers_provider_customer",
        table_name="billing_customers",
    )
    op.drop_index("ix_billing_customers_user_id", table_name="billing_customers")
    op.drop_table("billing_customers")
