"""add profile fields to users

Revision ID: c1f8a7e6d2b4
Revises: 9d3e9c3a1b72
Create Date: 2026-02-28 11:45:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1f8a7e6d2b4"
down_revision = "9d3e9c3a1b72"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))
    op.add_column(
        "users", sa.Column("mobile_number", sa.String(length=32), nullable=True)
    )
    op.add_column(
        "users", sa.Column("mobile_verified_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_unique_constraint("uq_users_mobile_number", "users", ["mobile_number"])


def downgrade() -> None:
    op.drop_constraint("uq_users_mobile_number", "users", type_="unique")
    op.drop_column("users", "mobile_verified_at")
    op.drop_column("users", "mobile_number")
    op.drop_column("users", "full_name")
