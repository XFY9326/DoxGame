from game_core import Player, Board, TurnBasedBoard, SimultaneousBoard
from game_players import HumanPlayer, SmartComputerPlayer, RandomComputerPlayer, is_computer_players
from game_ui import print_divider, print_game_panel, print_winner, print_init_player, print_player_link, input_board_size, input_player_type, input_game_type
from game_utils import Line, PlayerType, GameType


def play_game():
    print("Dox game\n")
    board = _create_board()
    _play_game_board(board)
    _show_winner(board)


def _play_game_board(board: Board):
    if isinstance(board, TurnBasedBoard):
        _play_turn_based_game(board)
    elif isinstance(board, SimultaneousBoard):
        _play_simultaneous_game(board)
    else:
        raise SystemError(f"Unhandled board {board.board_name}!")


def _show_winner(board: Board):
    print_divider()
    print_game_panel(board)
    print()
    print_winner(board.get_winner())


def _play_turn_based_game(board: TurnBasedBoard):
    print_divider()
    print_init_player(board.get_current_player())
    while not board.is_game_finish():
        print_divider()
        player = board.get_current_player()
        if isinstance(player, HumanPlayer):
            print_game_panel(board)
            print()
            _next_turn(board)
        else:
            new_line = _next_turn(board)
            print_player_link(player, new_line)


def _next_turn(board: TurnBasedBoard) -> Line:
    while True:
        try:
            line = _get_player_line_in_turn(board.get_current_player())
            board.draw_line(line)
            return line
        except ValueError as e:
            print(e)


def _play_simultaneous_game(board: SimultaneousBoard):
    while not board.is_game_finish():
        players = board.get_current_players()
        if not is_computer_players(*players):
            print_divider()
            print_game_panel(board)
            print()
        line_players = _get_all_line_players_in_turn(players)
        conflict_lines = board.check_conflict_lines(line_players)
        if len(conflict_lines) != 0:
            print(f"Line {', '.join([str(i) for i in conflict_lines])} conflict!")
        else:
            board.draw_line_players(line_players)


def _create_board() -> Board:
    while True:
        board_size = input_board_size()
        print()
        player_type = input_player_type()
        print()
        if player_type == PlayerType.HUMANS:
            players = [HumanPlayer("A"), HumanPlayer("B")]
            game_type = GameType.TURN_BASED
        elif player_type == PlayerType.HUMAN_AND_RANDOM_COMPUTER:
            players = [HumanPlayer("A"), RandomComputerPlayer("B")]
            game_type = input_game_type()
        elif player_type == PlayerType.HUMAN_AND_SMART_COMPUTER:
            players = [HumanPlayer("A"), SmartComputerPlayer("B")]
            game_type = input_game_type()
        else:
            raise SystemError(f"Unhandled player type {player_type}!")
        try:
            if game_type == GameType.TURN_BASED:
                return TurnBasedBoard(board_size, players)
            elif game_type == GameType.SIMULTANEOUS:
                return SimultaneousBoard(board_size, players)
            else:
                raise SystemError(f"Unhandled game type {player_type}!")
        except ValueError as e:
            print(e)


def _get_all_line_players_in_turn(players: list[Player]) -> dict[Line, list[Player]]:
    line_players: dict[Line, list[Player]] = {}
    for player in players:
        new_line = _get_player_line_in_turn(player)
        line_players.setdefault(new_line, []).append(player)
        if is_computer_players(player):
            print_divider()
            print_player_link(player, new_line)
    return line_players


def _get_player_line_in_turn(player: Player) -> Line:
    while True:
        line = player.in_turn()
        board = player.get_game_board()
        if board.has_line(line):
            print(f"Input line {line} already exists!")
        elif not board.check_line(line):
            print(f"Input invalid line {line}!")
        else:
            return line
