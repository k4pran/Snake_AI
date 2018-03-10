from enum import Enum


class Directions(Enum):
    UP = 0
    RIGHT = 90
    DOWN = 180
    LEFT = 270

    @staticmethod
    def get_opposite(direction):

        if direction == Directions.UP:
            return Directions.DOWN

        elif direction == Directions.RIGHT:
            return Directions.LEFT

        elif direction == Directions.DOWN:
            return Directions.UP

        elif direction == Directions.LEFT:
            return Directions.RIGHT

0
