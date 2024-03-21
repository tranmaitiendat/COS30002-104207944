import random
WIN_SET = (
	(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
	(1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)
)

class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.ai_player = None

    def display_board(self):
        for i in range(3):
            print('|'.join(self.board[i][j] for j in range(3)))
            print('-' * 5)

    def get_player_input(self):
        while True:
            try:
                move = int(input(f"Player {self.current_player}, Players is X enter your move (1-9): "))
                if 1 <= move <= 9:
                    row = (move - 1) // 3
                    col = (move - 1) % 3
                    if self.board[row][col] == ' ':
                        return row, col
                    else:
                        print("That position is already taken. Please choose another.")
                else:
                    print("Invalid move. Please choose a number between 1 and 9.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def update_board(self, move):
        row, col = move
        self.board[row][col] = self.current_player

    def check_win(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != ' ':
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return True
        return False

    def check_draw(self):
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False
        return True

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def set_ai_player(self, ai_player):
        self.ai_player = ai_player

    def play(self):
        print("Welcome to Tic-Tac-Toe!")
        print("Player 1 is X and Player 2 is O.")
        print("The board is numbered as follows:")
        print("1|2|3")
        print("-----")
        print("4|5|6")
        print("-----")
        print("7|8|9")
        print("Let's start!")

        while True:
            self.display_board()
            print(f"Player {self.current_player}'s turn. AI turn is O")
            if self.current_player == 'X':
                move = self.get_player_input()
            else:
                move = self.ai_player.make_move(self.board)
                print(f"AI chooses position {move[0] * 3 + move[1] + 1}")
            self.update_board(move)
            if self.check_win():
                self.display_board()
                print(f"{self.current_player} wins!")
                break
            elif self.check_draw():
                self.display_board()
                print("It's a draw!")
                break
            self.switch_player()


class RandomAI:
    def make_move(self, board):
        available_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']
        return random.choice(available_moves)


if __name__ == "__main__":
    game = TicTacToe()
    ai = RandomAI()
    game.set_ai_player(ai)
    game.play()
