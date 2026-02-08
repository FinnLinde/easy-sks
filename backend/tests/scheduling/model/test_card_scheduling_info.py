from datetime import datetime, timezone
from uuid import UUID

from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState


class TestCardSchedulingInfoDefaults:
    def test_generates_valid_uuid(self):
        info = CardSchedulingInfo()
        UUID(info.card_id)  # raises if not a valid UUID

    def test_default_state_is_new(self):
        info = CardSchedulingInfo()
        assert info.state == CardState.NEW

    def test_default_due_is_utc(self):
        info = CardSchedulingInfo()
        assert info.due.tzinfo == timezone.utc

    def test_default_numeric_fields_are_zero(self):
        info = CardSchedulingInfo()
        assert info.stability == 0.0
        assert info.difficulty == 0.0
        assert info.elapsed_days == 0
        assert info.scheduled_days == 0
        assert info.reps == 0
        assert info.lapses == 0

    def test_default_last_review_is_none(self):
        info = CardSchedulingInfo()
        assert info.last_review is None


class TestCardSchedulingInfoCustomValues:
    def test_custom_fields_are_preserved(self):
        due = datetime(2025, 6, 1, tzinfo=timezone.utc)
        last_review = datetime(2025, 5, 1, tzinfo=timezone.utc)

        info = CardSchedulingInfo(
            card_id="custom-id",
            state=CardState.REVIEW,
            stability=5.5,
            difficulty=3.2,
            elapsed_days=10,
            scheduled_days=30,
            reps=5,
            lapses=1,
            due=due,
            last_review=last_review,
        )

        assert info.card_id == "custom-id"
        assert info.state == CardState.REVIEW
        assert info.stability == 5.5
        assert info.difficulty == 3.2
        assert info.elapsed_days == 10
        assert info.scheduled_days == 30
        assert info.reps == 5
        assert info.lapses == 1
        assert info.due == due
        assert info.last_review == last_review
