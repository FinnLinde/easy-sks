from datetime import datetime, timezone

from fsrs import Card as FsrsCard
from fsrs import Rating as FsrsRating
from fsrs import ReviewLog as FsrsReviewLog
from fsrs import State as FsrsState

from scheduling.mapper.fsrs_mapper import FsrsMapper
from scheduling.model.card_scheduling_info import CardSchedulingInfo
from scheduling.model.card_state import CardState
from scheduling.model.rating import Rating


class TestCardStateMapping:
    def test_all_states_map_to_fsrs_and_back(self):
        for state in CardState:
            fsrs_state = FsrsMapper.to_fsrs_card(
                CardSchedulingInfo(state=state)
            ).state
            round_tripped = FsrsMapper.to_card_scheduling_info(
                FsrsCard(state=fsrs_state), card_id="x"
            ).state
            assert round_tripped == state


class TestRatingMapping:
    def test_all_ratings_map_to_fsrs_and_back(self):
        for rating in Rating:
            fsrs_rating = FsrsMapper.to_fsrs_rating(rating)
            assert FsrsMapper.to_rating(fsrs_rating) == rating

    def test_specific_rating_values(self):
        assert FsrsMapper.to_fsrs_rating(Rating.AGAIN) == FsrsRating.Again
        assert FsrsMapper.to_fsrs_rating(Rating.HARD) == FsrsRating.Hard
        assert FsrsMapper.to_fsrs_rating(Rating.GOOD) == FsrsRating.Good
        assert FsrsMapper.to_fsrs_rating(Rating.EASY) == FsrsRating.Easy


class TestCardRoundTrip:
    def test_round_trip_preserves_all_fields(self):
        due = datetime(2025, 6, 1, tzinfo=timezone.utc)
        last_review = datetime(2025, 5, 1, tzinfo=timezone.utc)

        original = CardSchedulingInfo(
            card_id="my-uuid",
            state=CardState.REVIEW,
            stability=4.5,
            difficulty=6.7,
            elapsed_days=10,
            scheduled_days=30,
            reps=3,
            lapses=1,
            due=due,
            last_review=last_review,
        )

        fsrs_card = FsrsMapper.to_fsrs_card(original)
        restored = FsrsMapper.to_card_scheduling_info(fsrs_card, card_id="my-uuid")

        assert restored.card_id == original.card_id
        assert restored.state == original.state
        assert restored.stability == original.stability
        assert restored.difficulty == original.difficulty
        assert restored.elapsed_days == original.elapsed_days
        assert restored.scheduled_days == original.scheduled_days
        assert restored.reps == original.reps
        assert restored.lapses == original.lapses
        assert restored.due == original.due
        assert restored.last_review == original.last_review


class TestReviewLogMapping:
    def test_maps_fsrs_review_log_to_domain(self):
        review_time = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)
        fsrs_log = FsrsReviewLog(
            rating=FsrsRating.Good,
            scheduled_days=0,
            elapsed_days=0,
            review=review_time,
            state=FsrsState.New,
        )

        log = FsrsMapper.to_review_log(fsrs_log, card_id="abc-123")

        assert log.card_id == "abc-123"
        assert log.rating == Rating.GOOD
        assert log.reviewed_at == review_time
        assert log.review_duration_ms is None
