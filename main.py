from game_manager import play_game


def main():
    play_game()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExit game")
