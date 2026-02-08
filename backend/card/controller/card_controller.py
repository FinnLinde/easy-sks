"""FastAPI router for card endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from card.model.card import Card
from study.service.card_repository_port import CardRepositoryPort

router = APIRouter(tags=["Cards"])


# -- Response schemas ------------------------------------------------------


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


def _card_to_out(card: Card) -> CardOut:
    return CardOut(
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
    )


# -- Dependency injection placeholder -------------------------------------


def get_card_repository() -> CardRepositoryPort:
    raise NotImplementedError("Must be overridden via app.dependency_overrides")


# -- Endpoints -------------------------------------------------------------


@router.get("/cards/{card_id}", response_model=CardOut)
async def get_card(
    card_id: str,
    card_repo: CardRepositoryPort = Depends(get_card_repository),
) -> CardOut:
    card = await card_repo.get_by_id(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card {card_id!r} not found")
    return _card_to_out(card)
