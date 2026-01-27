from __future__ import annotations

from dataclasses import dataclass
import math

from .enums import ReviewRating

# Default parameters and target retention match fsrs 6.3.0 Scheduler defaults.
DEFAULT_PARAMETERS: tuple[float, ...] = (
    0.212,
    1.2931,
    2.3065,
    8.2956,
    6.4133,
    0.8334,
    3.0194,
    0.001,
    1.8722,
    0.1666,
    0.796,
    1.4835,
    0.0614,
    0.2629,
    1.6483,
    0.6014,
    1.8729,
    0.5425,
    0.0912,
    0.0658,
    0.1542,
)
DEFAULT_TARGET_RETENTION = 0.9

MIN_DIFFICULTY = 1.0
MAX_DIFFICULTY = 10.0

# Use GOOD as the baseline rating for initializing new cards.
DEFAULT_INITIAL_RATING = ReviewRating.GOOD


def _to_fsrs_rating(rating: ReviewRating) -> int:
    return rating.value + 1


def initial_stability(
    rating: ReviewRating = DEFAULT_INITIAL_RATING,
    parameters: tuple[float, ...] = DEFAULT_PARAMETERS,
) -> float:
    fsrs_rating = _to_fsrs_rating(rating)
    return float(parameters[fsrs_rating - 1])


def initial_difficulty(
    rating: ReviewRating = DEFAULT_INITIAL_RATING,
    parameters: tuple[float, ...] = DEFAULT_PARAMETERS,
) -> float:
    fsrs_rating = _to_fsrs_rating(rating)
    difficulty = parameters[4] - (math.e ** (parameters[5] * (fsrs_rating - 1))) + 1
    return max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, float(difficulty)))


DEFAULT_INITIAL_STABILITY = initial_stability()
DEFAULT_INITIAL_DIFFICULTY = initial_difficulty()


@dataclass(frozen=True)
class FsrsMemoryState:
    stability: float
    difficulty: float


def default_memory_state() -> FsrsMemoryState:
    return FsrsMemoryState(
        stability=DEFAULT_INITIAL_STABILITY,
        difficulty=DEFAULT_INITIAL_DIFFICULTY,
    )
