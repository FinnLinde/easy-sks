"""initial schema

Revision ID: 6ef04772ae3b
Revises: 
Create Date: 2026-02-08 19:04:23.748008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ef04772ae3b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("card_id", sa.String(36), primary_key=True),
        sa.Column("front_text", sa.Text, nullable=False, server_default=""),
        sa.Column("front_images", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("answer_text", sa.Text, nullable=False, server_default=""),
        sa.Column("answer_images", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("short_answer", sa.JSON, nullable=False, server_default="[]"),
        sa.Column(
            "tags",
            sa.dialects.postgresql.ARRAY(sa.String),
            nullable=False,
            server_default="{}",
        ),
    )

    op.create_table(
        "card_scheduling_info",
        sa.Column("card_id", sa.String(36), primary_key=True),
        sa.Column("state", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("stability", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("difficulty", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("elapsed_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("scheduled_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reps", sa.Integer, nullable=False, server_default="0"),
        sa.Column("lapses", sa.Integer, nullable=False, server_default="0"),
        sa.Column("due", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_review", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "review_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("card_id", sa.String(36), nullable=False, index=True),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("review_duration_ms", sa.Integer, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("review_logs")
    op.drop_table("card_scheduling_info")
    op.drop_table("cards")
