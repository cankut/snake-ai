import enum
import numpy as np
import string
import random
from collections import namedtuple

class DIRECTION(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class TURN(enum.Enum):
    NONE = 0
    LEFT = -1
    RIGHT = 1


class BOARD_OBJECT(enum.Enum):
    EMPTY = 0
    BODY = 1
    TAIL = -1
    APPLE = 2

ALL_DIRECTIONS = [DIRECTION.UP, DIRECTION.RIGHT, DIRECTION.DOWN, DIRECTION.LEFT]
ALL_TURNS = [TURN.NONE, TURN.LEFT, TURN.RIGHT]

DIRECTION_UNIT_VECTORS = dict(
    [
        (DIRECTION.UP, [0, -1]),
        (DIRECTION.DOWN, [0, 1]),
        (DIRECTION.LEFT, [-1, 0]),
        (DIRECTION.RIGHT, [1, 0]),
    ]
)

DIRECTION_MARKERS = dict(
    [
        (DIRECTION.UP, '^'),
        (DIRECTION.DOWN, 'v'),
        (DIRECTION.LEFT, '<'),
        (DIRECTION.RIGHT, '>'),
    ]
)

LOG_LEVEL_THRESHOLD = 1

chars = string.ascii_letters + string.digits

def generate_id():
    return ''.join([random.choice(chars) for n in range(6)]) 

def generate_chromosome(length):
    return np.random.uniform(-1, 1, length)

def Log(message: str, level = 1, end='\n'):
    if(level >= LOG_LEVEL_THRESHOLD):
        print(message, end=end)