"""FastAPI router for study endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.model.role import Role
from auth.service.auth_dependencies import require_role
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating
from study.model.sks_topic import SksTopic
from study.model.study_card import StudyCard
from study.service.study_service import StudyService
from user.model.app_user import AppUser

router = APIRouter(tags=["Study"], dependencies=[require_role(Role.FREEMIUM)])


# -- Response / Request schemas --------------------------------------------


class CardImageOut(BaseModel):
    image_id: str
    storage_key: str
    alt_text: Optional[str] = None


class CardContentOut(BaseModel):
    text: str
    images: list[CardImageOut]


class CardOut(BaseModel):
    card_id: str
    front: CardContentOut
    answer: CardContentOut
    short_answer: list[str]
    tags: list[str]


class SchedulingInfoOut(BaseModel):
    state: str
    stability: float
    difficulty: float
    reps: int
    lapses: int
    due: str
    last_review: Optional[str] = None


class StudyCardOut(BaseModel):
    card: CardOut
    scheduling_info: SchedulingInfoOut


class TopicOut(BaseModel):
    value: str
    label: str


class ReviewIn(BaseModel):
    card_id: str
    rating: int  # 1=Again, 2=Hard, 3=Good, 4=Easy


class DashboardSummaryOut(BaseModel):
    due_now: int
    reviewed_today: int
    streak_days: int
    due_by_topic: dict[str, int]
    recommended_topic: Optional[str] = None
    available_cards: int


# -- Helpers ---------------------------------------------------------------

_TOPIC_LABELS: dict[str, str] = {
    "navigation": "Navigation",
    "schifffahrtsrecht": "Schifffahrtsrecht",
    "wetterkunde": "Wetterkunde",
    "seemannschaft_i": "Seemannschaft I",
    "seemannschaft_ii": "Seemannschaft II",
}

_STATE_NAMES: dict[CardState, str] = {
    CardState.NEW: "NEW",
    CardState.LEARNING: "LEARNING",
    CardState.REVIEW: "REVIEW",
    CardState.RELEARNING: "RELEARNING",
}


def _study_card_to_out(sc: StudyCard) -> StudyCardOut:
    card = sc.card
    info = sc.scheduling_info
    return StudyCardOut(
        card=CardOut(
            card_id=card.card_id,
            front=CardContentOut(
                text=card.front.text,
                images=[
                    CardImageOut(
                        image_id=img.image_id,
                        storage_key=img.storage_key,
                        alt_text=img.alt_text,
                    )
                    for img in card.front.images
                ],
            ),
            answer=CardContentOut(
                text=card.answer.text,
                images=[
                    CardImageOut(
                        image_id=img.image_id,
                        storage_key=img.storage_key,
                        alt_text=img.alt_text,
                    )
                    for img in card.answer.images
                ],
            ),
            short_answer=card.short_answer,
            tags=card.tags,
        ),
        scheduling_info=SchedulingInfoOut(
            state=_STATE_NAMES[info.state],
            stability=info.stability,
            difficulty=info.difficulty,
            reps=info.reps,
            lapses=info.lapses,
            due=info.due.isoformat(),
            last_review=info.last_review.isoformat() if info.last_review else None,
        ),
    )


# -- Dependency injection placeholder -------------------------------------
# The actual dependency is wired in dependencies.py / main.py.


def get_study_service() -> StudyService:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


def get_current_app_user() -> AppUser:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


# -- Endpoints -------------------------------------------------------------


@router.get("/topics", response_model=list[TopicOut])
async def list_topics() -> list[TopicOut]:
    return [
        TopicOut(value=t.value, label=_TOPIC_LABELS[t.value])
        for t in SksTopic
    ]


@router.get("/study/due", response_model=list[StudyCardOut])
async def get_due_cards(
    topic: Optional[str] = None,
    study_service: StudyService = Depends(get_study_service),
    user: AppUser = Depends(get_current_app_user),
) -> list[StudyCardOut]:
    sks_topic: SksTopic | None = None
    if topic is not None:
        try:
            sks_topic = SksTopic(topic)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown topic: {topic}")

    due = await study_service.get_due_cards(user_id=user.id, topic=sks_topic)
    return [_study_card_to_out(sc) for sc in due]


@router.get("/study/practice", response_model=list[StudyCardOut])
async def get_practice_cards(
    topic: Optional[str] = None,
    study_service: StudyService = Depends(get_study_service),
    user: AppUser = Depends(get_current_app_user),
) -> list[StudyCardOut]:
    sks_topic: SksTopic | None = None
    if topic is not None:
        try:
            sks_topic = SksTopic(topic)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown topic: {topic}")

    cards = await study_service.get_practice_cards(user_id=user.id, topic=sks_topic)
    return [_study_card_to_out(sc) for sc in cards]


@router.post("/study/review", response_model=StudyCardOut)
async def review_card(
    body: ReviewIn,
    study_service: StudyService = Depends(get_study_service),
    user: AppUser = Depends(get_current_app_user),
) -> StudyCardOut:
    try:
        rating = Rating(body.rating)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid rating: {body.rating}")

    try:
        result = await study_service.review_card(
            user_id=user.id,
            card_id=body.card_id,
            rating=rating,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return _study_card_to_out(result)


@router.get("/dashboard/summary", response_model=DashboardSummaryOut)
async def get_dashboard_summary(
    study_service: StudyService = Depends(get_study_service),
    user: AppUser = Depends(get_current_app_user),
) -> DashboardSummaryOut:
    summary = await study_service.get_dashboard_summary(user_id=user.id)
    return DashboardSummaryOut(
        due_now=summary.due_now,
        reviewed_today=summary.reviewed_today,
        streak_days=summary.streak_days,
        due_by_topic=summary.due_by_topic,
        recommended_topic=summary.recommended_topic,
        available_cards=summary.available_cards,
    )
