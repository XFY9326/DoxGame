import abc
import random

from game_core import Player
from game_ui import input_line
from game_utils import Line


class HumanPlayer(Player):

    def in_turn(self) -> Line:
        return input_line(self)


class ComputerPlayer(Player):

    def _get_available_lines(self) -> list[Line]:
        board = self.get_game_board()
        result = []
        for x in range(board.max_row):
            for y in range(board.max_col - 1):
                line = Line((x, y), (x, y + 1))
                if not board.has_line(line):
                    result.append(line)
        for y in range(board.max_col):
            for x in range(board.max_row - 1):
                line = Line((x, y), (x + 1, y))
                if not board.has_line(line):
                    result.append(line)
        return result

    @abc.abstractmethod
    def in_turn(self) -> Line:
        raise NotImplementedError


class RandomComputerPlayer(ComputerPlayer):

    def in_turn(self) -> Line:
        available_lines = self._get_available_lines()
        random.shuffle(available_lines)
        return available_lines[0]


class SmartComputerPlayer(ComputerPlayer):

    def _calculate_line_score(self, line: Line) -> int:
        board = self.get_game_board()
        opposite_lines = board.generate_opposite_lines(line)
        score = 0
        for opposite_line in opposite_lines:
            side_line_1 = line.link_point_1(opposite_line)
            side_line_2 = line.link_point_2(opposite_line)
            exist_lines = list(filter(lambda x: board.has_line(x), [opposite_line, side_line_1, side_line_2]))
            if len(exist_lines) == 3:
                score += 3
            elif len(exist_lines) == 2:
                score -= 1
            elif len(exist_lines) == 1:
                score += 1
        return score

    def in_turn(self) -> Line:
        available_lines = self._get_available_lines()
        score_lines = [(self._calculate_line_score(i), i) for i in available_lines]
        score_lines = sorted(score_lines, key=lambda x: x[0], reverse=True)
        best_lines = [i for i in score_lines if score_lines[0][0] == i[0]]
        random.shuffle(best_lines)
        return best_lines[0][1]


def is_computer_players(*players: Player):
    return all([isinstance(p, ComputerPlayer) for p in players])
