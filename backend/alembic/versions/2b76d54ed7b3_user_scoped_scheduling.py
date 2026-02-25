"""make scheduling and review logs user scoped

Revision ID: 2b76d54ed7b3
Revises: 6ef04772ae3b
Create Date: 2026-02-25 22:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b76d54ed7b3"
down_revision: Union[str, None] = "6ef04772ae3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_USER_ID = "legacy-user"


def upgrade() -> None:
    # Add user scope to scheduling entries.
    op.add_column(
        "card_scheduling_info",
        sa.Column(
            "user_id",
            sa.String(length=255),
            nullable=False,
            server_default=LEGACY_USER_ID,
        ),
    )
    op.drop_constraint(
        "card_scheduling_info_pkey", "card_scheduling_info", type_="primary"
    )
    op.create_primary_key(
        "card_scheduling_info_pkey",
        "card_scheduling_info",
        ["user_id", "card_id"],
    )
    op.create_index(
        "ix_card_scheduling_info_user_id_due",
        "card_scheduling_info",
        ["user_id", "due"],
        unique=False,
    )
    op.alter_column("card_scheduling_info", "user_id", server_default=None)

    # Add user scope to review logs to support per-user analytics/dashboard.
    op.add_column(
        "review_logs",
        sa.Column(
            "user_id",
            sa.String(length=255),
            nullable=False,
            server_default=LEGACY_USER_ID,
        ),
    )
    op.create_index("ix_review_logs_user_id", "review_logs", ["user_id"], unique=False)
    op.create_index(
        "ix_review_logs_user_id_reviewed_at",
        "review_logs",
        ["user_id", "reviewed_at"],
        unique=False,
    )
    op.alter_column("review_logs", "user_id", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_review_logs_user_id_reviewed_at", table_name="review_logs")
    op.drop_index("ix_review_logs_user_id", table_name="review_logs")
    op.drop_column("review_logs", "user_id")

    op.drop_index(
        "ix_card_scheduling_info_user_id_due", table_name="card_scheduling_info"
    )
    op.drop_constraint(
        "card_scheduling_info_pkey", "card_scheduling_info", type_="primary"
    )
    op.create_primary_key(
        "card_scheduling_info_pkey", "card_scheduling_info", ["card_id"]
    )
    op.drop_column("card_scheduling_info", "user_id")

