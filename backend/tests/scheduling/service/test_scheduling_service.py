from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating
from scheduling.service.scheduling_service import SchedulingService


class TestReviewCard:
    def test_new_card_transitions_after_review(self):
        service = SchedulingService()
        card = CardSchedulingInfo()

        updated, log = service.review_card(card, Rating.GOOD)

        assert updated.state != CardState.NEW
        assert updated.stability > 0.0
        assert updated.difficulty > 0.0
        assert updated.reps == 1

    def test_preserves_card_id(self):
        service = SchedulingService()
        card = CardSchedulingInfo(card_id="keep-this-id")

        updated, log = service.review_card(card, Rating.EASY)

        assert updated.card_id == "keep-this-id"
        assert log.card_id == "keep-this-id"

    def test_review_log_records_rating(self):
        service = SchedulingService()
        card = CardSchedulingInfo()

        _, log = service.review_card(card, Rating.HARD)

        assert log.rating == Rating.HARD

    def test_due_date_advances_after_review(self):
        service = SchedulingService()
        card = CardSchedulingInfo()

        updated, _ = service.review_card(card, Rating.GOOD)

        assert updated.due > card.due


class TestGetRetrievability:
    def test_new_card_returns_zero(self):
        service = SchedulingService()
        card = CardSchedulingInfo()

        assert service.get_retrievability(card) == 0.0

    def test_reviewed_card_returns_positive_value(self):
        service = SchedulingService()
        card = CardSchedulingInfo()
        reviewed, _ = service.review_card(card, Rating.GOOD)

        r = service.get_retrievability(reviewed)

        assert 0.0 < r <= 1.0
