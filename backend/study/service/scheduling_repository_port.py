from __future__ import annotations

from datetime import datetime
from typing import Protocol

from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.review_log import ReviewLog


class SchedulingRepositoryPort(Protocol):
    """Port for retrieving and persisting card scheduling state."""

    async def list_all(self) -> list[CardSchedulingInfo]: ...

    async def get_by_card_id(self, card_id: str) -> CardSchedulingInfo | None: ...

    async def get_due(self, before: datetime) -> list[CardSchedulingInfo]: ...

    async def save(self, info: CardSchedulingInfo) -> None: ...

    async def save_review_log(self, log: ReviewLog) -> None: ...

    async def list_review_logs(self) -> list[ReviewLog]: ...
