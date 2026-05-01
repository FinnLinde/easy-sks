from __future__ import annotations

from typing import Protocol

from exam.model.exam_answer import ExamAnswer
from exam.model.exam_session import ExamSession


class ExamRepositoryPort(Protocol):
    """Port for exam session persistence."""

    async def create_session(self, session: ExamSession, answers: list[ExamAnswer]) -> None: ...

    async def get_session(self, session_id: str) -> ExamSession | None: ...

    async def save_session(self, session: ExamSession) -> None: ...

    async def list_answers(self, session_id: str) -> list[ExamAnswer]: ...

    async def get_answer(self, session_id: str, card_id: str) -> ExamAnswer | None: ...

    async def save_answer(self, answer: ExamAnswer) -> None: ...

    async def list_completed_sessions(self) -> list[ExamSession]: ...
