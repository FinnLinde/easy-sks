"""FastAPI router for exam simulation endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from exam.model.exam_session import ExamSessionDetails
from exam.model.exam_template import ExamTemplate
from exam.service.exam_service import ExamService

router = APIRouter(tags=["Exams"])


class CardImageOut(BaseModel):
    image_id: str
    storage_key: str
    alt_text: Optional[str] = None


class ExamTemplateOut(BaseModel):
    sheet_number: int
    display_name: str
    question_count: int
    time_limit_minutes: int


class ExamQuestionOut(BaseModel):
    question_number: int
    card_id: str
    question_text: str
    question_images: list[CardImageOut]
    student_answer: str
    answered_at: Optional[str] = None


class ExamSessionOut(BaseModel):
    session_id: str
    sheet_number: int
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    deadline_at: str
    time_limit_minutes: int
    time_remaining_seconds: int
    time_over: bool
    question_count: int
    questions: list[ExamQuestionOut]


class StartExamSessionIn(BaseModel):
    sheet_number: int = Field(..., ge=1, le=15)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1, le=240)


class SaveAnswerIn(BaseModel):
    student_answer: str = ""


class SaveAnswerOut(BaseModel):
    session_id: str
    card_id: str
    question_number: int
    student_answer: str
    answered_at: Optional[str] = None


class ExamQuestionResultOut(BaseModel):
    question_number: int
    card_id: str
    question_text: str
    reference_short_answer: list[str]
    student_answer: str
    score: float
    is_correct: bool
    feedback: str
    errors: list[str]


class ExamResultOut(BaseModel):
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
    questions: list[ExamQuestionResultOut]


class ExamSessionHistoryOut(BaseModel):
    session_id: str
    sheet_number: int
    status: str
    started_at: str
    submitted_at: Optional[str] = None
    total_score: Optional[float] = None
    max_score: Optional[float] = None
    passed: Optional[bool] = None
    time_over: bool


# -- Dependency injection placeholder -------------------------------------


def get_exam_service() -> ExamService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


# -- Endpoints -------------------------------------------------------------


@router.get("/exams", response_model=list[ExamTemplateOut])
async def list_exams(
    exam_service: ExamService = Depends(get_exam_service),
) -> list[ExamTemplateOut]:
    templates = await exam_service.list_templates()
    return [_template_to_out(template) for template in templates]


@router.post("/exam-sessions", response_model=ExamSessionOut)
async def start_exam_session(
    body: StartExamSessionIn,
    exam_service: ExamService = Depends(get_exam_service),
) -> ExamSessionOut:
    try:
        details = await exam_service.start_session(
            sheet_number=body.sheet_number,
            time_limit_minutes=body.time_limit_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _details_to_out(details)


@router.get("/exam-sessions", response_model=list[ExamSessionHistoryOut])
async def list_exam_history(
    exam_service: ExamService = Depends(get_exam_service),
) -> list[ExamSessionHistoryOut]:
    items = await exam_service.list_history()
    return [
        ExamSessionHistoryOut(
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


@router.get("/exam-sessions/{session_id}", response_model=ExamSessionOut)
async def get_exam_session(
    session_id: str,
    exam_service: ExamService = Depends(get_exam_service),
) -> ExamSessionOut:
    try:
        details = await exam_service.get_session_details(session_id=session_id)
    except ValueError as exc:
        raise _error_for_service_exception(exc)

    return _details_to_out(details)


@router.put("/exam-sessions/{session_id}/answers/{card_id}", response_model=SaveAnswerOut)
async def save_exam_answer(
    session_id: str,
    card_id: str,
    body: SaveAnswerIn,
    exam_service: ExamService = Depends(get_exam_service),
) -> SaveAnswerOut:
    try:
        answer = await exam_service.save_answer(
            session_id=session_id,
            card_id=card_id,
            student_answer=body.student_answer,
        )
    except ValueError as exc:
        raise _error_for_service_exception(exc)

    return SaveAnswerOut(
        session_id=answer.session_id,
        card_id=answer.card_id,
        question_number=answer.question_number,
        student_answer=answer.student_answer,
        answered_at=answer.answered_at.isoformat() if answer.answered_at else None,
    )


@router.post("/exam-sessions/{session_id}/submit", response_model=ExamResultOut)
async def submit_exam_session(
    session_id: str,
    exam_service: ExamService = Depends(get_exam_service),
) -> ExamResultOut:
    try:
        result = await exam_service.submit_session(session_id=session_id)
    except ValueError as exc:
        raise _error_for_service_exception(exc)

    return _result_to_out(result)


@router.get("/exam-sessions/{session_id}/result", response_model=ExamResultOut)
async def get_exam_result(
    session_id: str,
    exam_service: ExamService = Depends(get_exam_service),
) -> ExamResultOut:
    try:
        result = await exam_service.get_result(session_id=session_id)
    except ValueError as exc:
        raise _error_for_service_exception(exc)

    return _result_to_out(result)


# -- Helpers ---------------------------------------------------------------


def _template_to_out(template: ExamTemplate) -> ExamTemplateOut:
    return ExamTemplateOut(
        sheet_number=template.sheet_number,
        display_name=template.display_name,
        question_count=template.question_count,
        time_limit_minutes=template.time_limit_minutes,
    )


def _details_to_out(details: ExamSessionDetails) -> ExamSessionOut:
    session = details.session
    now = datetime.now(timezone.utc)
    deadline = session.deadline_at
    remaining = max(0, int((deadline - now).total_seconds()))
    time_over = session.time_over or session.is_time_over(now)

    return ExamSessionOut(
        session_id=session.id,
        sheet_number=session.sheet_number,
        status=session.status.value,
        started_at=session.started_at.isoformat(),
        submitted_at=session.submitted_at.isoformat() if session.submitted_at else None,
        deadline_at=deadline.isoformat(),
        time_limit_minutes=session.time_limit_minutes,
        time_remaining_seconds=remaining,
        time_over=time_over,
        question_count=len(details.questions),
        questions=[
            ExamQuestionOut(
                question_number=question.question_number,
                card_id=question.card.card_id,
                question_text=question.card.front.text,
                question_images=[
                    CardImageOut(
                        image_id=image.image_id,
                        storage_key=image.storage_key,
                        alt_text=image.alt_text,
                    )
                    for image in question.card.front.images
                ],
                student_answer=question.answer.student_answer,
                answered_at=(
                    question.answer.answered_at.isoformat()
                    if question.answer.answered_at
                    else None
                ),
            )
            for question in details.questions
        ],
    )


def _result_to_out(result) -> ExamResultOut:
    return ExamResultOut(
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
            ExamQuestionResultOut(
                question_number=question.question_number,
                card_id=question.card_id,
                question_text=question.question_text,
                reference_short_answer=question.reference_short_answer,
                student_answer=question.student_answer,
                score=question.score,
                is_correct=question.is_correct,
                feedback=question.feedback,
                errors=question.errors,
            )
            for question in result.questions
        ],
    )


def _error_for_service_exception(exc: ValueError) -> HTTPException:
    message = str(exc)
    status_code = 404 if "not found" in message else 400
    return HTTPException(status_code=status_code, detail=message)
