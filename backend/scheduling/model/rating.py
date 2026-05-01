from enum import IntEnum


class Rating(IntEnum):
    """Represents the four possible ratings when reviewing a card."""

    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4
