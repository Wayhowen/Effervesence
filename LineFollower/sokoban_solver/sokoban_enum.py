from enum import Enum
from telnetlib import GA


class ChoiceEnum(Enum):
    @classmethod
    def all(cls):
        return [x for x in cls]

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def names(cls):
        return tuple(x.name for x in cls)

    @classmethod
    def name_to_value(cls, name):
        for x in cls:
            if x.name == name:
                return x.value
        raise ValueError("Given name doesn't match any name from enum")


class GameObjects(ChoiceEnum):
    EMPTY = 1
    WALL = 2
    DIAMOND = 3
    GOAL = 4
    OCCUPIED_GOAL = 5
    PLAYER = 6

if __name__ == "__main__":
    print(GameObjects.choices())