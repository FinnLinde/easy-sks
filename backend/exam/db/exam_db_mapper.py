"""Maps between exam domain objects and ORM rows."""

from __future__ import annotations

from exam.db.exam_tables import ExamAnswerRow, ExamSessionRow
from exam.model.exam_answer import ExamAnswer
from exam.model.exam_session import ExamSession, ExamSessionStatus


class ExamDbMapper:
    """Stateless mapper between exam domain objects and table rows."""

    @staticmethod
    def session_to_domain(row: ExamSessionRow) -> ExamSession:
        return ExamSession(
            id=row.id,
            sheet_number=row.sheet_number,
            status=ExamSessionStatus(row.status),
            started_at=row.started_at,
            submitted_at=row.submitted_at,
            time_limit_minutes=row.time_limit_minutes,
            total_score=row.total_score,
            max_score=row.max_score,
            passed=row.passed,
            time_over=row.time_over,
        )

    @staticmethod
    def session_to_row(session: ExamSession) -> ExamSessionRow:
        return ExamSessionRow(
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
    def answer_to_domain(row: ExamAnswerRow) -> ExamAnswer:
        return ExamAnswer(
            id=row.id,
            session_id=row.session_id,
            card_id=row.card_id,
            question_number=row.question_number,
            student_answer=row.student_answer,
            answered_at=row.answered_at,
            score=row.score,
            is_correct=row.is_correct,
            feedback=row.feedback,
            errors=list(row.errors or []),
        )

    @staticmethod
    def answer_to_row(answer: ExamAnswer) -> ExamAnswerRow:
        return ExamAnswerRow(
            id=answer.id,
            session_id=answer.session_id,
            card_id=answer.card_id,
            question_number=answer.question_number,
            student_answer=answer.student_answer,
            answered_at=answer.answered_at,
            score=answer.score,
            is_correct=answer.is_correct,
            feedback=answer.feedback,
            errors=answer.errors,
        )
