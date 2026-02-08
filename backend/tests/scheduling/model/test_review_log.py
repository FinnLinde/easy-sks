from datetime import datetime, timezone

from scheduling.model.rating import Rating
from scheduling.model.review_log import ReviewLog


class TestReviewLog:
    def test_construction_with_required_fields(self):
        now = datetime.now(timezone.utc)
        log = ReviewLog(card_id="abc", rating=Rating.GOOD, reviewed_at=now)

        assert log.card_id == "abc"
        assert log.rating == Rating.GOOD
        assert log.reviewed_at == now

    def test_review_duration_defaults_to_none(self):
        now = datetime.now(timezone.utc)
        log = ReviewLog(card_id="abc", rating=Rating.EASY, reviewed_at=now)
        assert log.review_duration_ms is None

    def test_review_duration_is_preserved(self):
        now = datetime.now(timezone.utc)
        log = ReviewLog(
            card_id="abc", rating=Rating.HARD, reviewed_at=now, review_duration_ms=1500
        )
        assert log.review_duration_ms == 1500
