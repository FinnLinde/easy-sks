"""add navigation tasks, sessions, and answers tables

Revision ID: b7c2e4f1a839
Revises: 5a3d6a1e2f44
Create Date: 2026-03-05 21:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "b7c2e4f1a839"
down_revision: Union[str, None] = "5a3d6a1e2f44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "navigation_tasks",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("sheet_number", sa.Integer(), nullable=False),
        sa.Column("task_number", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("context", sa.Text(), nullable=False, server_default=""),
        sa.Column("sub_questions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("solution_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("key_answers", sa.JSON(), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("task_id"),
        sa.UniqueConstraint("sheet_number", "task_number", name="uq_nav_tasks_sheet_task"),
    )
    op.create_index("ix_navigation_tasks_sheet_number", "navigation_tasks", ["sheet_number"])

    op.create_table(
        "navigation_sessions",
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
        sa.Column("time_over", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_navigation_sessions_user_id", "navigation_sessions", ["user_id"])

    op.create_table(
        "navigation_answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("task_number", sa.Integer(), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=False, server_default=""),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["navigation_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["task_id"], ["navigation_tasks.task_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "task_id", name="uq_nav_answers_session_task"),
    )
    op.create_index("ix_navigation_answers_session_id", "navigation_answers", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_navigation_answers_session_id", table_name="navigation_answers")
    op.drop_table("navigation_answers")

    op.drop_index("ix_navigation_sessions_user_id", table_name="navigation_sessions")
    op.drop_table("navigation_sessions")

    op.drop_index("ix_navigation_tasks_sheet_number", table_name="navigation_tasks")
    op.drop_table("navigation_tasks")
