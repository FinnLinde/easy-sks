from enum import Enum, IntEnum


class CardState(str, Enum):
    NEW = "NEW"
    REVIEW = "REVIEW"
    SUSPENDED = "SUSPENDED"


class ReviewRating(IntEnum):
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3
