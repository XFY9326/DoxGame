import re

from game_core import Board, Player
from game_utils import Line, PlayerType, GameType

_LINE_1_REGEX = re.compile(r"^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$")
_LINE_2_REGEX = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
_SIZE_REGEX = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*$")


def input_line(player: Player) -> Line:
    print(f"Entre the pairs to connect for {player}. Format: '(x1,y1)(x2,y2)' or 'x1 y1 x2 y2'")
    while True:
        content = input("Input: ").strip()
        pattern = _LINE_1_REGEX.fullmatch(content)
        if pattern is None:
            pattern = _LINE_2_REGEX.fullmatch(content)
        if pattern is not None:
            px1, py1, px2, py2 = pattern.groups()
            try:
                return Line((int(px1) - 1, int(py1) - 1), (int(px2) - 1, int(py2) - 1))
            except ValueError as e:
                print(e)
        else:
            print("Wrong input format!")


def input_board_size() -> tuple[int, int]:
    print("Enter the board rows/columns. Format: 'rows,columns'")
    while True:
        content = input("Input: ").strip()
        pattern = _SIZE_REGEX.fullmatch(content)
        if pattern is not None:
            rows, columns = pattern.groups()
            rows, columns = int(rows), int(columns)
            if rows > 3 and columns > 3:
                return rows, columns
            else:
                print(f"Size ({rows},{columns}) too small!")
        else:
            print("Wrong input format!")


def input_player_type() -> PlayerType:
    print("Enter player type:")
    print("1 -> Human players")
    print("2 -> Human player and Random Computer player")
    print("3 -> Human player and Smart Computer player")
    while True:
        content = input("Input: ").strip()
        try:
            choice = int(content)
            if choice == 1:
                return PlayerType.HUMANS
            elif choice == 2:
                return PlayerType.HUMAN_AND_RANDOM_COMPUTER
            elif choice == 3:
                return PlayerType.HUMAN_AND_SMART_COMPUTER
            else:
                print(f"Unknown choice {choice}")
        except ValueError:
            print("Wrong input!")


def input_game_type() -> GameType:
    print("Enter game type:")
    print("1 -> Turn-based")
    print("2 -> Simultaneous")
    while True:
        content = input("Input: ").strip()
        try:
            choice = int(content)
            if choice == 1:
                return GameType.TURN_BASED
            elif choice == 2:
                return GameType.SIMULTANEOUS
            else:
                print(f"Unknown choice {choice}")
        except ValueError:
            print("Wrong input!")


def print_init_player(player: Player):
    print(f"{player} is randomly selected to start.")


def print_winner(players: list[Player]):
    if len(players) == 0:
        print("Game over")
    elif len(players) == 1:
        print(f"{players[0]} win! Score: {players[0].score}")
    else:
        print(f"Player {', '.join([p.player_name for p in players])} tie! Score: {players[0].score}")


def print_divider(size: int = 40):
    print("\n" + "-" * size + "\n")


def print_scores(board: Board):
    print("Scores:", ", ".join([f"{p.player_name}: {p.score:.1f}" for p in board.players]))


def print_player_link(player: Player, line: Line):
    print(f"{player} draw line {line}")


def print_board(board: Board):
    print("  x")
    for r in range(board.max_row * 2):
        if r == 0:
            print("y   " + "   ".join([str(i + 1) for i in range(board.max_col)]), end='')
        elif r % 2 == 0:
            print("  ", end='')
            px1 = r // 2 - 1
            px2 = px1 + 1
            for c in range(board.max_col * 2):
                if c == 0:
                    print("  ", end='')
                elif c % 2 == 0:
                    py = c // 2 - 1
                    box_player = board.find_box_players(px1, py)
                    if box_player is None:
                        print("  ", end='')
                    elif len(box_player[1]) == 1:
                        print(f"{box_player[1][0].player_name} ", end='')
                    else:
                        print(f"@ ", end='')
                else:
                    py = c // 2
                    if board.has_points_line((px1, py), (px2, py)):
                        print("| ", end='')
                    else:
                        print("  ", end='')
        else:
            print("  ", end='')
            px = r // 2
            for c in range(board.max_col * 2):
                if c == 0:
                    print(f"{px + 1} ", end='')
                elif c % 2 == 0:
                    py1 = c // 2 - 1
                    py2 = py1 + 1
                    if board.has_points_line((px, py1), (px, py2)):
                        print("---", end='')
                    else:
                        print("   ", end='')
                else:
                    print("*", end='')
        print()


def print_game_panel(board: Board):
    print_board(board)
    print()
    print_scores(board)
