from enum import Enum

class Result(Enum):
    WIN = 1
    HALF_WIN = 0.5
    LOSS = -1
    HALF_LOSS = -0.5
    DRAW = 0