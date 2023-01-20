import enum
from typing import Union
from itertools import chain


class PlayerType(str, enum.Enum):
    HUMANS = "HUMANS"
    HUMAN_AND_RANDOM_COMPUTER = "HUMAN_AND_RANDOM_COMPUTER"
    HUMAN_AND_SMART_COMPUTER = "HUMAN_AND_SMART_COMPUTER"


class GameType(str, enum.Enum):
    TURN_BASED = "TURN_BASED"
    SIMULTANEOUS = "SIMULTANEOUS"


class Point:
    # x -> row  y -> col
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def in_range(self, left: int, top: int, right: int, bottom: int) -> bool:
        return top <= self.x <= bottom and left <= self.y <= right

    def offset(self, offset_x: int = 0, offset_y: int = 0) -> 'Point':
        return Point(self.x + offset_x, self.y + offset_y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return self.__repr__()

    def __repr__(self) -> str:
        return f"({self.x + 1},{self.y + 1})"


class Line:
    def __init__(self, p1: Union[Point, tuple[int, int]], p2: Union[Point, tuple[int, int]]):
        if isinstance(p1, tuple):
            p1 = Point(p1[0], p1[1])
        if isinstance(p2, tuple):
            p2 = Point(p2[0], p2[1])
        if p1 == p2:
            raise ValueError(f"Points {p1} and {p2} can't make a line!")
        if p1.x + p1.y < p2.x + p2.y:
            self._p1: Point = p1
            self._p2: Point = p2
        else:
            self._p1: Point = p2
            self._p2: Point = p1

    def in_range(self, left: int, top: int, right: int, bottom: int) -> bool:
        return self._p1.in_range(left, top, right, bottom) and self._p2.in_range(left, top, right, bottom)

    def offset(self, offset_x: int = 0, offset_y: int = 0) -> 'Line':
        return Line(self._p1.offset(offset_x, offset_y), self._p2.offset(offset_x, offset_y))

    @property
    def point_1(self):
        return self._p1

    @property
    def point_2(self):
        return self._p2

    def link_point_1(self, other: 'Line') -> 'Line':
        return Line(self.point_1, other.point_1)

    def link_point_2(self, other: 'Line') -> 'Line':
        return Line(self.point_2, other.point_2)

    def is_vertical(self) -> bool:
        return self._p1.y == self._p2.y and self._p1.x != self._p2.x

    def is_horizontal(self) -> bool:
        return self._p1.x == self._p2.x and self._p1.y != self._p2.y

    def __hash__(self):
        return hash((self._p1, self._p2))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.point_1 == other.point_1 and self.point_2 == other.point_2

    def __str__(self):
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self._p1}~{self._p2}"


class Box(Point):

    @staticmethod
    def from_points(points: list[Point]) -> 'Box':
        points = set(points)
        if len(points) != 4:
            raise ValueError(f"Box must have 4 different point! Current: {len(points)}")
        sorted_points: list[tuple[int, Point]] = sorted([(p.x + p.y, p) for p in points], key=lambda x: x[0])
        if sorted_points[0][0] < sorted_points[1][0] == sorted_points[2][0] < sorted_points[3][0] and \
                sorted_points[3][0] - sorted_points[2][0] == sorted_points[1][0] - sorted_points[0][0]:
            return Box(sorted_points[0][1].x, sorted_points[0][1].y)
        else:
            raise ValueError(f"These 4 points can't make a box! \
            {sorted_points[0][1]}, {sorted_points[1][1]}, {sorted_points[2][1]}, {sorted_points[3][1]}")

    @staticmethod
    def from_lines(lines: list[Line]) -> 'Box':
        lines = set(lines)
        if len(lines) != 4:
            raise ValueError(f"Box must have 4 different lines! Current: {len(lines)}")
        return Box.from_points(list(chain.from_iterable([(line.point_1, line.point_2) for line in lines])))
