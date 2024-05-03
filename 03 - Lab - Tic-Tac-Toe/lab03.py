import random

class TicTacToe:
    def __init__(self, player1, player2):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.players = {"X": player1, "O": player2}
        self.current_player = "X"
        self.winner = None
        print(f"The starting player is: {self.players[self.current_player]}")

    def check_winner(self):
        # Check rows
        for row in self.board:
            if all(cell == row[0] for cell in row) and row[0] != " ":
                return row[0]

        # Check columns
        for col in zip(*self.board):
            if all(cell == col[0] for cell in col) and col[0] != " ":
                return col[0]

        # Check diagonals
        if all(self.board[i][i] == self.board[0][0] for i in range(3)) and self.board[0][0] != " ":
            return self.board[0][0]
        if all(self.board[i][2-i] == self.board[0][2] for i in range(3)) and self.board[0][2] != " ":
            return self.board[0][2]

        # Check for a tie
        if all(cell != " " for row in self.board for cell in row):
            return "Tie"

        return None

    def get_human_move(self):
        while True:
            row = int(input("Enter the row (0-2): "))
            col = int(input("Enter the column (0-2): "))
            if self.board[row][col] == " ":
                return row, col
            print("Invalid move. Please try again.")

    def get_first_bot_move(self):
        while True:
            row, col = random.randint(0, 2), random.randint(0, 2)
            if self.board[row][col] == " ":
                return row, col

    def get_second_bot_move(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == " ":
                    return row, col

    def get_move(self, player):
        if player == "Human":
            return self.get_human_move()
        elif player == "FirstBot":
            return self.get_first_bot_move()
        elif player == "SecondBot":
            return self.get_second_bot_move()

    def process_input(self):
        player = self.players[self.current_player]
        self.move = self.get_move(player)

    def update(self):
        row, col = self.move
        self.board[row][col] = self.current_player
        self.winner = self.check_winner()
        self.current_player = "O" if self.current_player == "X" else "X"

    def render(self):
        self.display_board()
        print("=====================")
        if not self.winner:
            print(f"The current player is: {self.players[self.current_player]}")

    def display_board(self):
        for row in self.board:
            print(" | ".join(row))
            print("-" * 9)

    def display_result(self):
        print("=====================")
        print("===== GAME OVER =====")
        if self.winner == "Tie":
            print("It's a tie!")
        else:
            print(f"{self.players[self.winner]} is the winner!")

game = TicTacToe("FirstBot", "SecondBot")

while not game.winner:
    game.process_input()
    game.update()
    game.render()

game.display_result()
