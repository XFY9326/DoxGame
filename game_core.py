import abc
import math
import random
from typing import Union, Optional

from game_utils import Line, Point, Box


class Board:
    def __init__(self, size: tuple[int, int], players: list['Player']):
        self._validate_size(size)
        self._validate_players(players)
        self.max_row = size[0]
        self.max_col = size[1]
        self.players: list[Player] = players
        for player in self.players:
            player.join_game(self)
        self.lines: set[Line] = set()
        self.boxes: dict[Box, list[Player]] = {}

    @property
    def board_name(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def _validate_size(size: tuple[int, int]):
        if size[0] <= 3 or size[1] <= 3:
            raise ValueError(f"Size ({size[0]},{size[1]}) too small!")

    @staticmethod
    def _validate_players(players: list['Player']):
        if len(players) != len(set(players)):
            raise ValueError("Same name players exists!")
        elif len(players) < 2:
            raise ValueError("Player amount should greater than 1!")

    def reset(self):
        self.lines = []
        self.boxes = {}
        for player in self.players:
            player.reset()

    def get_winner(self) -> list['Player']:
        if self.is_game_finish():
            all_players = sorted(self.players, key=lambda x: x.score, reverse=True)
            return [p for p in all_players if math.fabs(p.score - all_players[0].score) < 0.01]
        else:
            raise SystemError("Game is running!")

    def check_line(self, line: Line) -> bool:
        return line.in_range(0, 0, self.max_col - 1, self.max_row - 1) and \
            abs((line.point_1.x + line.point_1.y) - (line.point_2.x + line.point_2.y)) == 1

    def has_line(self, line: Line) -> bool:
        return self.check_line(line) and line in self.lines

    def has_points_line(self, p1: Union[Point, tuple[int, int]], p2: Union[Point, tuple[int, int]]) -> bool:
        return self.has_line(Line(p1, p2))

    def has_box(self, box: Box) -> bool:
        return box.in_range(0, 0, self.max_col - 2, self.max_row - 2) and box in self.boxes

    def find_box_players(self, x: int, y: int) -> Optional[tuple[Box, list['Player']]]:
        for box, players in self.boxes.items():
            if box.x == x and box.y == y:
                return box, players
        return None

    def is_game_finish(self) -> bool:
        all_lines = (self.max_row - 1) * self.max_col + (self.max_col - 1) * self.max_row
        all_boxes = (self.max_col - 1) * (self.max_row - 1)
        has_all_lines = len(self.lines) == all_lines
        has_all_boxes = len(self.boxes) == all_boxes
        if has_all_lines != has_all_boxes:
            raise SystemError(f"Game lines and boxes status error! Lines: {len(self.lines)}/{all_lines} Boxes: {len(self.boxes)}/{all_boxes}")
        return has_all_lines and has_all_boxes

    @staticmethod
    def generate_opposite_lines(line: Line) -> list[Line]:
        if line.is_vertical():
            opposite_lines = [line.offset(offset_y=-1), line.offset(offset_y=1)]
        elif line.is_horizontal():
            opposite_lines = [line.offset(offset_x=-1), line.offset(offset_x=1)]
        else:
            raise ValueError(f"Invalid line {line}!")
        return opposite_lines

    def _make_available_new_boxes(self, line: Line) -> list[Box]:
        opposite_lines = self.generate_opposite_lines(line)
        result = []
        for opposite_line in opposite_lines:
            if self.has_line(opposite_line):
                side_lines = [line.link_point_1(opposite_line), line.link_point_2(opposite_line)]
                if all([self.has_line(i) for i in side_lines]):
                    result.append(Box.from_lines([line, opposite_line] + side_lines))
        return result

    def can_make_boxes(self, line: Line) -> bool:
        return len(self._make_available_new_boxes(line)) > 0

    def _generate_new_boxes(self, line: Line, players: list['Player']) -> dict[Box, list['Player']]:
        new_boxes = self._make_available_new_boxes(line)
        if len(new_boxes) == 0:
            return {}
        return dict(zip(new_boxes, [players] * len(new_boxes)))

    def _add_new_line_players(self, line: Line, players: list['Player']) -> dict[Box, list['Player']]:
        if line in self.lines:
            raise ValueError(f"Line {line} already exists!")
        elif not self.check_line(line):
            raise ValueError(f"Invalid line {line}!")
        else:
            new_boxes = self._generate_new_boxes(line, players)
            self.boxes.update(new_boxes)
            self.lines.add(line)
            for player in players:
                player.add_score(len(new_boxes) / len(players))
                player.add_moves(line)
            return new_boxes


class TurnBasedBoard(Board):
    def __init__(self, size: tuple[int, int], players: list['Player']):
        super().__init__(size, players)
        self._current_player_index: int = random.randint(0, len(self.players) - 1)

    def get_current_player(self) -> 'Player':
        if 0 <= self._current_player_index < len(self.players):
            return self.players[self._current_player_index]
        else:
            raise ValueError(f"Wrong player index {self._current_player_index} in {len(self.players)}!")

    def _next_turn(self) -> 'Player':
        if 0 <= self._current_player_index < len(self.players):
            if self._current_player_index == len(self.players) - 1:
                self._current_player_index = 0
            else:
                self._current_player_index += 1
            return self.players[self._current_player_index]
        else:
            raise ValueError(f"Wrong player index {self._current_player_index} in {len(self.players)}!")

    def draw_line(self, line: Line):
        new_boxes = self._add_new_line_players(line, [self.get_current_player()])
        if len(new_boxes) == 0:
            self._next_turn()


class SimultaneousBoard(Board):
    def __init__(self, size: tuple[int, int], players: list['Player']):
        super().__init__(size, players)
        self._continue_players: set[Player] = set()

    def get_current_players(self):
        if len(self._continue_players) == 0 or len(self._continue_players) == len(self.players):
            return self.players
        else:
            return self._continue_players

    def check_conflict_lines(self, line_players: dict[Line, list['Player']]) -> list[Line]:
        conflict_lines = []
        for line, players in line_players.items():
            if len(players) > 1 and not self.can_make_boxes(line):
                conflict_lines.append(line)
        return conflict_lines

    def draw_line_players(self, line_players: dict[Line, list['Player']]):
        self._continue_players.clear()
        for line, players in line_players.items():
            if len(self._add_new_line_players(line, players)) > 0:
                self._continue_players.update(players)


class Player(abc.ABC):
    def __init__(self, name: str):
        self._name: str = name
        self._score: float = 0.0
        self.moves: list[Line] = []
        self._board: Optional[Board] = None

    def join_game(self, board: Board):
        self._board = board

    def get_game_board(self) -> Board:
        if self._board is None:
            raise SystemError(f"{self} didn't join any game!")
        else:
            return self._board

    @property
    def player_name(self):
        return self._name

    @property
    def player_type(self):
        return self.__class__.__name__

    @property
    def score(self):
        if self._board is None:
            raise SystemError(f"{self} didn't join any game!")
        return self._score

    def reset(self):
        self._score = 0
        self.moves = []

    def add_score(self, step: float = 1.0):
        if self._board is None:
            raise SystemError(f"{self} didn't join any game!")
        self._score += step

    def add_moves(self, line: Line):
        if self._board is None:
            raise SystemError(f"{self} didn't join any game!")
        self.moves.append(line)

    @abc.abstractmethod
    def in_turn(self) -> Line:
        raise NotImplementedError

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._name == other._name

    def __str__(self):
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.player_type} {self.player_name}"
