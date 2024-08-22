from enum import Enum, auto


class Command(Enum):
    train = auto()
    score = auto()
    whitelist = auto()
