"""add user foreign keys to scheduling and review logs

Revision ID: 9d3e9c3a1b72
Revises: 8f91bd2ab1aa
Create Date: 2026-02-27 17:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d3e9c3a1b72"
down_revision: Union[str, None] = "8f91bd2ab1aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Backfill local users for any existing user-scoped rows before adding FKs.
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, auth_provider, auth_provider_user_id, email)
            SELECT DISTINCT s.user_id, 'legacy', s.user_id, NULL
            FROM card_scheduling_info s
            LEFT JOIN users u ON u.id = s.user_id
            WHERE u.id IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, auth_provider, auth_provider_user_id, email)
            SELECT DISTINCT r.user_id, 'legacy', r.user_id, NULL
            FROM review_logs r
            LEFT JOIN users u ON u.id = r.user_id
            WHERE u.id IS NULL
            """
        )
    )

    op.create_foreign_key(
        "fk_card_scheduling_info_user_id_users",
        "card_scheduling_info",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_review_logs_user_id_users",
        "review_logs",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_review_logs_user_id_users",
        "review_logs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_card_scheduling_info_user_id_users",
        "card_scheduling_info",
        type_="foreignkey",
    )
