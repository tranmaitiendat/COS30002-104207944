import random

WINNING_SET = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
    [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]
]

def display(game_boards):
    for i in range(0, 9, 3):
        print(f"{game_boards[i]} | {game_boards[i + 1]} | {game_boards[i + 2]}")
        if i < 6:
            print("---------")

def victory_check(game_boards, player):
    return any(all(game_boards[pos] == player for pos in win_set) for win_set in WINNING_SET)

def full_boards(game_boards):
    return all(cell != ' ' for cell in game_boards)

def valid_move(move, game_boards):
    return 1 <= move <= 9 and game_boards[move - 1] == ' '

def available_moves(game_boards):
    return [i + 1 for i, cell in enumerate(game_boards) if cell == ' ']

def winning_move(game_boards, player):
    for win_set in WINNING_SET:
        count_player = win_set.count(player)
        count_empty = win_set.count(' ')
        if count_player == 2 and count_empty == 1:
            return next(move + 1 for move, cell in enumerate(win_set) if cell == ' ')

    return None

def strategic_moves(game_boards):
    preferred_moves = [5, 3, 1, 7, 9,2 ,4 ,8 , 6]

    for move in preferred_moves:
        if move in available_moves(game_boards):
            return move

def play_game():
    game_boards = [' '] * 9
    current_players = 'X'

    while True:
        display(game_boards)

        if current_players == 'X':
            move = int(input(f"Player {current_players}, choose a move from 1 to 9: "))
            if not valid_move(move, game_boards):
                print("it have a problem. Please try again.")
                continue
        else:
            print("AI is calculating its move...")
            winnings = winning_move(game_boards, 'O')
            blockings = winning_move(game_boards, 'X')

            move = winnings or blockings or strategic_moves(game_boards)

        game_boards[move - 1] = current_players

        if victory_check(game_boards, current_players):
            display(game_boards)
            if current_players == 'X':
                print("Player X wins this game!")
            else:
                print("AI wins this game!")
            break
        elif full_boards(game_boards):
            display(game_boards)
            print("It's a tie!")
            break

        current_players = 'O' if current_players == 'X' else 'X'

if __name__ == "__main__":
    play_game()
