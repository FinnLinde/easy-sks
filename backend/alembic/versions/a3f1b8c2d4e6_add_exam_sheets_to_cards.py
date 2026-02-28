"""add exam_sheets to cards

Revision ID: a3f1b8c2d4e6
Revises: c1f8a7e6d2b4
Create Date: 2026-02-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a3f1b8c2d4e6"
down_revision: Union[str, None] = "c1f8a7e6d2b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cards",
        sa.Column(
            "exam_sheets",
            postgresql.ARRAY(sa.Integer()),
            server_default="{}",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("cards", "exam_sheets")
