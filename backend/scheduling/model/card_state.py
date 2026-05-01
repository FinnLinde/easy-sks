from enum import IntEnum


class CardState(IntEnum):
    """Represents the learning state of a card in the scheduling system."""

    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3
