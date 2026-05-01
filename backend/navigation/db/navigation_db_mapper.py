"""Maps between navigation domain objects and ORM rows."""

from __future__ import annotations

from navigation.db.navigation_tables import NavigationAnswerRow, NavigationSessionRow, NavigationTaskRow
from navigation.model.navigation_answer import NavigationAnswer
from navigation.model.navigation_session import NavigationSession, NavigationSessionStatus
from navigation.model.navigation_task import NavigationTask, SubQuestion


class NavigationDbMapper:
    """Stateless mapper between navigation domain objects and database rows."""

    @staticmethod
    def task_to_domain(row: NavigationTaskRow) -> NavigationTask:
        return NavigationTask(
            task_id=row.task_id,
            sheet_number=row.sheet_number,
            task_number=row.task_number,
            points=row.points,
            context=row.context,
            sub_questions=[
                SubQuestion(text=sq["text"], points=sq.get("points", 1))
                for sq in (row.sub_questions or [])
            ],
            solution_text=row.solution_text,
            key_answers=row.key_answers or [],
        )

    @staticmethod
    def task_to_row(task: NavigationTask) -> NavigationTaskRow:
        return NavigationTaskRow(
            task_id=task.task_id,
            sheet_number=task.sheet_number,
            task_number=task.task_number,
            points=task.points,
            context=task.context,
            sub_questions=[
                {"text": sq.text, "points": sq.points} for sq in task.sub_questions
            ],
            solution_text=task.solution_text,
            key_answers=task.key_answers,
        )

    @staticmethod
    def session_to_domain(row: NavigationSessionRow) -> NavigationSession:
        return NavigationSession(
            id=row.id,
            sheet_number=row.sheet_number,
            status=NavigationSessionStatus(row.status),
            started_at=row.started_at,
            submitted_at=row.submitted_at,
            time_limit_minutes=row.time_limit_minutes,
            total_score=row.total_score,
            max_score=row.max_score,
            passed=row.passed,
            time_over=row.time_over,
        )

    @staticmethod
    def session_to_row(session: NavigationSession) -> NavigationSessionRow:
        return NavigationSessionRow(
            id=session.id,
            sheet_number=session.sheet_number,
            status=session.status.value,
            started_at=session.started_at,
            submitted_at=session.submitted_at,
            time_limit_minutes=session.time_limit_minutes,
            total_score=session.total_score,
            max_score=session.max_score,
            passed=session.passed,
            time_over=session.time_over,
        )

    @staticmethod
    def answer_to_domain(row: NavigationAnswerRow) -> NavigationAnswer:
        return NavigationAnswer(
            id=row.id,
            session_id=row.session_id,
            task_id=row.task_id,
            task_number=row.task_number,
            student_answer=row.student_answer,
            answered_at=row.answered_at,
            score=row.score,
            is_correct=row.is_correct,
            feedback=row.feedback,
        )

    @staticmethod
    def answer_to_row(answer: NavigationAnswer) -> NavigationAnswerRow:
        return NavigationAnswerRow(
            id=answer.id,
            session_id=answer.session_id,
            task_id=answer.task_id,
            task_number=answer.task_number,
            student_answer=answer.student_answer,
            answered_at=answer.answered_at,
            score=answer.score,
            is_correct=answer.is_correct,
            feedback=answer.feedback,
        )
