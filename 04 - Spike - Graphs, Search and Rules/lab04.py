import math
import random

class TicTacToe:
    def __init__(self, player1, player2):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.players = {"X": player1, "O": player2}
        self.turn = 0
        self.winner = None
        self.current_player = "X"
        self.history = []
        print(f"Turn: {self.turn}. Current player: {self.players[self.current_player]}")

    def check_winner(self, board):
        # Check rows, columns, and diagonals for a winner
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != " ":
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != " ":
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return board[0][2]
        if all(cell != " " for row in board for cell in row):
            return "Tie"
        return None

    def get_human_move(self):
        while True:
            row = int(input("Enter row (0-2): "))
            col = int(input("Enter column (0-2): "))
            if self.board[row][col] == " ":
                return row, col
            print("Invalid move. Try again.")

    def get_random_move(self):
        while True:
            row, col = random.randint(0, 2), random.randint(0, 2)
            if self.board[row][col] == " ":
                return row, col

    def get_priority_move(self):
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == " ":
                    return row, col

    def get_possible_moves(self, board):
        return [(row, col) for row in range(3) for col in range(3) if board[row][col] == " "]

    def get_random_search_move(self):
        temp_board = [row[:] for row in self.board]
        moves = self.get_possible_moves(temp_board)
        random.shuffle(moves)

        best_eval = -math.inf
        best_move = None

        for row, col in moves:
            initial_board = [row[:] for row in temp_board]
            temp_board[row][col] = self.current_player
            opponent = "X" if self.current_player == "O" else "O"
            if self.check_winner(temp_board) is None:
                opp_row, opp_col = self.get_random_move()
            eval = self.random_search(temp_board, self.current_player)
            if eval > best_eval:
                best_eval = eval
                best_move = (row, col)
            temp_board = initial_board

        return best_move

    def random_search(self, board, player):
        winner = self.check_winner(board)
        if winner == player:
            return 1
        elif winner == "Tie":
            return 0
        elif winner is not None:
            return -1

        moves = self.get_possible_moves(board)
        random.shuffle(moves)
        max_eval = -math.inf

        for row, col in moves:
            initial_board = [row[:] for row in board]
            board[row][col] = player
            opponent = "X" if player == "O" else "O"
            if self.check_winner(board) is None:
                opp_row, opp_col = self.get_random_move()
            eval = self.random_search(board, player)
            board = initial_board
            max_eval = max(max_eval, eval)

        return max_eval

    def get_minimax_move(self):
        temp_board = [row[:] for row in self.board]
        moves = self.get_possible_moves(temp_board)
        random.shuffle(moves)

        best_eval = -math.inf
        best_move = None

        for row, col in moves:
            initial_board = [row[:] for row in temp_board]
            temp_board[row][col] = self.current_player
            opponent = "X" if self.current_player == "O" else "O"
            eval = self.minimax(temp_board, 0, self.current_player, opponent, -math.inf, math.inf)
            if eval > best_eval:
                best_eval = eval
                best_move = (row, col)
            temp_board = initial_board

        return best_move

    def minimax(self, board, depth, initial_player, current_player, alpha, beta):
        winner = self.check_winner(board)
        if winner == initial_player:
            return 1
        elif winner == "Tie":
            return 0
        elif winner is not None:
            return -1

        moves = self.get_possible_moves(board)
        random.shuffle(moves)

        if current_player != initial_player:
            min_eval = math.inf
            for row, col in moves:
                initial_board = [row[:] for row in board]
                board[row][col] = current_player
                next_player = "X" if current_player == "O" else "O"
                eval = self.minimax(board, depth + 1, initial_player, next_player, alpha, beta)
                board = initial_board
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        else:
            max_eval = -math.inf
            for row, col in moves:
                initial_board = [row[:] for row in board]
                board[row][col] = current_player
                next_player = "X" if current_player == "O" else "O"
                eval = self.minimax(board, depth + 1, initial_player, next_player, alpha, beta)
                board = initial_board
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

    def get_move(self, player):
        if player == "Human":
            return self.get_human_move()
        elif player == "FirstBot":
            return self.get_random_move()
        elif player == "SecondBot":
            return self.get_priority_move()
        elif player == "ThirdBot":
            return self.get_random_search_move()
        elif player in ["FourthBot", "FifthBot"]:
            return self.get_minimax_move()

    def process_input(self):
        self.move = self.get_move(self.players[self.current_player])

    def update(self):
        row, col = self.move
        self.board[row][col] = self.current_player
        self.winner = self.check_winner(self.board)
        self.current_player = "O" if self.current_player == "X" else "X"
        self.turn += 1

    def render(self):
        self.display_board()
        print("=====================")
        if self.winner is None:
            print(f"Turn: {self.turn}. Current player: {self.players[self.current_player]}")

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
            print(f"{self.players[self.winner]} wins!")

game = TicTacToe("ThirdBot", "FifthBot")

while game.winner is None:
    game.process_input()
    game.update()
    game.render()

game.display_result()