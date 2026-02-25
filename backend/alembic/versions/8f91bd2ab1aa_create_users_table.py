"""create local users table

Revision ID: 8f91bd2ab1aa
Revises: 2b76d54ed7b3
Create Date: 2026-02-25 22:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f91bd2ab1aa"
down_revision: Union[str, None] = "2b76d54ed7b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=255), primary_key=True),
        sa.Column("auth_provider", sa.String(length=32), nullable=False),
        sa.Column("auth_provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "auth_provider_user_id", name="uq_users_auth_provider_user_id"
        ),
    )
    op.create_index("ix_users_auth_provider_user_id", "users", ["auth_provider_user_id"])

    # Ensure the legacy placeholder referenced by the ESKS-001 migration can be
    # represented as a local user before later FK constraints are introduced.
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, auth_provider, auth_provider_user_id, email)
            VALUES (:id, :provider, :provider_user_id, NULL)
            ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(
            id="legacy-user",
            provider="legacy",
            provider_user_id="legacy-user",
        )
    )


def downgrade() -> None:
    op.drop_index("ix_users_auth_provider_user_id", table_name="users")
    op.drop_table("users")

