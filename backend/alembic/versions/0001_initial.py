"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-30 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
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
            postgresql.ARRAY(sa.String),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "exam_sheets",
            postgresql.ARRAY(sa.Integer),
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
    op.create_index(
        "ix_card_scheduling_info_due",
        "card_scheduling_info",
        ["due"],
    )

    op.create_table(
        "review_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("card_id", sa.String(36), nullable=False, index=True),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column(
            "reviewed_at", sa.DateTime(timezone=True), nullable=False, index=True
        ),
        sa.Column("review_duration_ms", sa.Integer, nullable=True),
    )

    op.create_table(
        "exam_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sheet_number", sa.Integer, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_limit_minutes", sa.Integer, nullable=False),
        sa.Column("total_score", sa.Float, nullable=True),
        sa.Column("max_score", sa.Float, nullable=True),
        sa.Column("passed", sa.Boolean, nullable=True),
        sa.Column(
            "time_over", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
    )

    op.create_table(
        "exam_answers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("exam_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "card_id",
            sa.String(36),
            sa.ForeignKey("cards.card_id"),
            nullable=False,
        ),
        sa.Column("question_number", sa.Integer, nullable=False),
        sa.Column("student_answer", sa.Text, nullable=False, server_default=""),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("errors", sa.JSON, nullable=False, server_default="[]"),
        sa.UniqueConstraint(
            "session_id", "card_id", name="uq_exam_answers_session_card"
        ),
    )
    op.create_index(
        "ix_exam_answers_session_id", "exam_answers", ["session_id"]
    )
    op.create_index(
        "ix_exam_answers_session_question",
        "exam_answers",
        ["session_id", "question_number"],
    )

    op.create_table(
        "navigation_tasks",
        sa.Column("task_id", sa.String(36), primary_key=True),
        sa.Column("sheet_number", sa.Integer, nullable=False),
        sa.Column("task_number", sa.Integer, nullable=False),
        sa.Column("points", sa.Integer, nullable=False),
        sa.Column("context", sa.Text, nullable=False, server_default=""),
        sa.Column("sub_questions", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("solution_text", sa.Text, nullable=False, server_default=""),
        sa.Column("key_answers", sa.JSON, nullable=False, server_default="[]"),
        sa.UniqueConstraint(
            "sheet_number", "task_number", name="uq_nav_tasks_sheet_task"
        ),
    )
    op.create_index(
        "ix_navigation_tasks_sheet_number", "navigation_tasks", ["sheet_number"]
    )

    op.create_table(
        "navigation_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sheet_number", sa.Integer, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_limit_minutes", sa.Integer, nullable=False),
        sa.Column("total_score", sa.Float, nullable=True),
        sa.Column("max_score", sa.Float, nullable=True),
        sa.Column("passed", sa.Boolean, nullable=True),
        sa.Column(
            "time_over", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
    )

    op.create_table(
        "navigation_answers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("navigation_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "task_id",
            sa.String(36),
            sa.ForeignKey("navigation_tasks.task_id"),
            nullable=False,
        ),
        sa.Column("task_number", sa.Integer, nullable=False),
        sa.Column("student_answer", sa.Text, nullable=False, server_default=""),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.UniqueConstraint(
            "session_id", "task_id", name="uq_nav_answers_session_task"
        ),
    )
    op.create_index(
        "ix_navigation_answers_session_id", "navigation_answers", ["session_id"]
    )

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column(
            "ai_enabled", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
        sa.Column("openai_api_key", sa.Text, nullable=True),
        sa.Column(
            "openai_chat_model",
            sa.String(128),
            nullable=False,
            server_default="gpt-4o-mini",
        ),
        sa.Column(
            "openai_transcription_model",
            sa.String(128),
            nullable=False,
            server_default="gpt-4o-mini-transcribe",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.execute(
        "INSERT INTO app_settings (id, ai_enabled, openai_chat_model, "
        "openai_transcription_model) VALUES (1, false, 'gpt-4o-mini', "
        "'gpt-4o-mini-transcribe') ON CONFLICT DO NOTHING"
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_index("ix_navigation_answers_session_id", table_name="navigation_answers")
    op.drop_table("navigation_answers")
    op.drop_table("navigation_sessions")
    op.drop_index("ix_navigation_tasks_sheet_number", table_name="navigation_tasks")
    op.drop_table("navigation_tasks")
    op.drop_index("ix_exam_answers_session_question", table_name="exam_answers")
    op.drop_index("ix_exam_answers_session_id", table_name="exam_answers")
    op.drop_table("exam_answers")
    op.drop_table("exam_sessions")
    op.drop_table("review_logs")
    op.drop_index("ix_card_scheduling_info_due", table_name="card_scheduling_info")
    op.drop_table("card_scheduling_info")
    op.drop_table("cards")
