"""add exam sessions and answers tables

Revision ID: e6b4c1d9f7a2
Revises: a3f1b8c2d4e6
Create Date: 2026-02-28
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "e6b4c1d9f7a2"
down_revision: Union[str, None] = "a3f1b8c2d4e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exam_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("sheet_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("time_over", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exam_sessions_user_id", "exam_sessions", ["user_id"])

    op.create_table(
        "exam_answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("card_id", sa.String(length=36), nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=False, server_default=""),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("errors", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.ForeignKeyConstraint(["card_id"], ["cards.card_id"]),
        sa.ForeignKeyConstraint(["session_id"], ["exam_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "card_id", name="uq_exam_answers_session_card"),
    )
    op.create_index("ix_exam_answers_session_id", "exam_answers", ["session_id"])
    op.create_index(
        "ix_exam_answers_session_question",
        "exam_answers",
        ["session_id", "question_number"],
    )


def downgrade() -> None:
    op.drop_index("ix_exam_answers_session_question", table_name="exam_answers")
    op.drop_index("ix_exam_answers_session_id", table_name="exam_answers")
    op.drop_table("exam_answers")

    op.drop_index("ix_exam_sessions_user_id", table_name="exam_sessions")
    op.drop_table("exam_sessions")
