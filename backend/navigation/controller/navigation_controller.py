"""FastAPI router for navigation exam endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from navigation.service.navigation_service import NavigationService, NavigationTemplate

router = APIRouter(tags=["Navigation"])


# -- Request / Response schemas --------------------------------------------


class NavigationTemplateOut(BaseModel):
    sheet_number: int
    display_name: str
    task_count: int
    total_points: int
    time_limit_minutes: int


class SubQuestionOut(BaseModel):
    text: str
    points: int


class NavigationQuestionOut(BaseModel):
    task_number: int
    task_id: str
    points: int
    context: str
    sub_questions: list[SubQuestionOut]
    student_answer: str
    answered_at: Optional[str] = None


class NavigationSessionOut(BaseModel):
    session_id: str
    sheet_number: int
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    deadline_at: str
    time_limit_minutes: int
    time_remaining_seconds: int
    time_over: bool
    task_count: int
    questions: list[NavigationQuestionOut]


class StartNavigationSessionIn(BaseModel):
    sheet_number: int = Field(..., ge=1, le=10)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1, le=240)


class SaveNavigationAnswerIn(BaseModel):
    student_answer: str = ""


class SaveNavigationAnswerOut(BaseModel):
    session_id: str
    task_id: str
    task_number: int
    student_answer: str
    answered_at: Optional[str] = None


class NavigationQuestionResultOut(BaseModel):
    task_number: int
    task_id: str
    context: str
    sub_questions: list[str]
    key_answers: list[str]
    solution_text: str
    student_answer: str
    score: float
    max_score: float
    is_correct: bool
    feedback: str


class NavigationResultOut(BaseModel):
    session_id: str
    sheet_number: int
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    time_limit_minutes: int
    time_over: bool
    total_score: float
    max_score: float
    passed: bool
    pass_score_threshold: float
    questions: list[NavigationQuestionResultOut]


class NavigationSessionHistoryOut(BaseModel):
    session_id: str
    sheet_number: int
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    passed: Optional[bool] = None
    time_over: bool


# -- Dependency injection placeholder --------------------------------------


def get_navigation_service() -> NavigationService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


# -- Endpoints -------------------------------------------------------------


@router.get("/navigation-exams", response_model=list[NavigationTemplateOut])
async def list_navigation_exams(
    service: NavigationService = Depends(get_navigation_service),
) -> list[NavigationTemplateOut]:
    templates = await service.list_templates()
    return [_template_to_out(t) for t in templates]


@router.post("/navigation-sessions", response_model=NavigationSessionOut)
async def start_navigation_session(
    body: StartNavigationSessionIn,
    service: NavigationService = Depends(get_navigation_service),
) -> NavigationSessionOut:
    try:
        details = await service.start_session(
            sheet_number=body.sheet_number,
            time_limit_minutes=body.time_limit_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _details_to_out(details)


@router.get("/navigation-sessions", response_model=list[NavigationSessionHistoryOut])
async def list_navigation_history(
    service: NavigationService = Depends(get_navigation_service),
) -> list[NavigationSessionHistoryOut]:
    items = await service.list_history()
    return [
        NavigationSessionHistoryOut(
            session_id=item.session_id,
            sheet_number=item.sheet_number,
            status=item.status,
            started_at=item.started_at.isoformat(),
            submitted_at=item.submitted_at.isoformat() if item.submitted_at else None,
            total_score=item.total_score,
            max_score=item.max_score,
            passed=item.passed,
            time_over=item.time_over,
        )
        for item in items
    ]


@router.get("/navigation-sessions/{session_id}", response_model=NavigationSessionOut)
async def get_navigation_session(
    session_id: str,
    service: NavigationService = Depends(get_navigation_service),
) -> NavigationSessionOut:
    try:
        details = await service.get_session_details(session_id=session_id)
    except ValueError as exc:
        raise _error_for(exc)
    return _details_to_out(details)


@router.put(
    "/navigation-sessions/{session_id}/answers/{task_id}",
    response_model=SaveNavigationAnswerOut,
)
async def save_navigation_answer(
    session_id: str,
    task_id: str,
    body: SaveNavigationAnswerIn,
    service: NavigationService = Depends(get_navigation_service),
) -> SaveNavigationAnswerOut:
    try:
        answer = await service.save_answer(
            session_id=session_id,
            task_id=task_id,
            student_answer=body.student_answer,
        )
    except ValueError as exc:
        raise _error_for(exc)
    return SaveNavigationAnswerOut(
        session_id=answer.session_id,
        task_id=answer.task_id,
        task_number=answer.task_number,
        student_answer=answer.student_answer,
        answered_at=answer.answered_at.isoformat() if answer.answered_at else None,
    )


@router.post(
    "/navigation-sessions/{session_id}/submit",
    response_model=NavigationResultOut,
)
async def submit_navigation_session(
    session_id: str,
    service: NavigationService = Depends(get_navigation_service),
) -> NavigationResultOut:
    try:
        result = await service.submit_session(session_id=session_id)
    except ValueError as exc:
        raise _error_for(exc)
    return _result_to_out(result)


@router.get(
    "/navigation-sessions/{session_id}/result",
    response_model=NavigationResultOut,
)
async def get_navigation_result(
    session_id: str,
    service: NavigationService = Depends(get_navigation_service),
) -> NavigationResultOut:
    try:
        result = await service.get_result(session_id=session_id)
    except ValueError as exc:
        raise _error_for(exc)
    return _result_to_out(result)


# -- Helpers ---------------------------------------------------------------


def _template_to_out(t: NavigationTemplate) -> NavigationTemplateOut:
    return NavigationTemplateOut(
        sheet_number=t.sheet_number,
        display_name=t.display_name,
        task_count=t.task_count,
        total_points=t.total_points,
        time_limit_minutes=t.time_limit_minutes,
    )


def _details_to_out(details) -> NavigationSessionOut:
    session = details.session
    now = datetime.now(timezone.utc)
    deadline = session.deadline_at
    remaining = max(0, int((deadline - now).total_seconds()))
    time_over = session.time_over or session.is_time_over(now)

    return NavigationSessionOut(
        session_id=session.id,
        sheet_number=session.sheet_number,
        status=session.status.value,
        started_at=session.started_at.isoformat(),
        submitted_at=session.submitted_at.isoformat() if session.submitted_at else None,
        deadline_at=deadline.isoformat(),
        time_limit_minutes=session.time_limit_minutes,
        time_remaining_seconds=remaining,
        time_over=time_over,
        task_count=len(details.questions),
        questions=[
            NavigationQuestionOut(
                task_number=q.task_number,
                task_id=q.task.task_id,
                points=q.task.points,
                context=q.task.context,
                sub_questions=[
                    SubQuestionOut(text=sq.text, points=sq.points)
                    for sq in q.task.sub_questions
                ],
                student_answer=q.answer.student_answer,
                answered_at=(
                    q.answer.answered_at.isoformat() if q.answer.answered_at else None
                ),
            )
            for q in details.questions
        ],
    )


def _result_to_out(result) -> NavigationResultOut:
    return NavigationResultOut(
        session_id=result.session_id,
        sheet_number=result.sheet_number,
        status=result.status,
        started_at=result.started_at.isoformat(),
        submitted_at=result.submitted_at.isoformat() if result.submitted_at else None,
        time_limit_minutes=result.time_limit_minutes,
        time_over=result.time_over,
        total_score=result.total_score,
        max_score=result.max_score,
        passed=result.passed,
        pass_score_threshold=result.pass_score_threshold,
        questions=[
            NavigationQuestionResultOut(
                task_number=q.task_number,
                task_id=q.task_id,
                context=q.context,
                sub_questions=q.sub_questions,
                key_answers=q.key_answers,
                solution_text=q.solution_text,
                student_answer=q.student_answer,
                score=q.score,
                max_score=q.max_score,
                is_correct=q.is_correct,
                feedback=q.feedback,
            )
            for q in result.questions
        ],
    )


def _error_for(exc: ValueError) -> HTTPException:
    message = str(exc)
    status_code = 404 if "not found" in message else 400
    return HTTPException(status_code=status_code, detail=message)
