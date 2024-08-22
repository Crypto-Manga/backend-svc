from enum import Enum, auto


class GameOutcome(Enum):

    DETECTION_INCREASE = auto()
    DETECTION_DECREASE = auto()

    MIRROR = auto()
