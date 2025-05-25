import chess
from typing import Optional, Tuple

class Board:
    def __init__(self):
        self.board = chess.Board()

    def print_board(self) -> None:
        """Print the current board state."""
        print("\n" + str(self.board) + "\n")

    def get_move_from_user(self) -> Tuple[Optional[chess.Move], str]:
        """Get a move from the user in SAN format."""
        while True:
            move_san = input("Enter your move (e.g., 'e4', 'Nf3'), or ask for 'help', 'play', or 'exit': ").strip()
            if move_san.lower() in ("help", "play", "exit"):
                return None, move_san.lower()
            try:
                move = self.board.parse_san(move_san)
                return move, ""
            except chess.AmbiguousMoveError:
                print("Ambiguous move! Be more specific (e.g., 'Rae1' for rook from a-file, 'Rhe1' for rook from h-file)")
            except chess.IllegalMoveError:
                print("Illegal move! Try again.")
            except chess.InvalidMoveError:
                print("Invalid move format! Try again.")

    def make_move(self, move: chess.Move) -> bool:
        """Make a move on the board."""
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def get_board(self) -> chess.Board:
        """Return the current board state."""
        return self.board

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()

    def get_game_result(self) -> Optional[chess.Outcome]:
        """Get the result of the game if it's over."""
        if not self.is_game_over():
            return None
        return self.board.outcome()

    def get_move_san(self, move: chess.Move) -> str:
        """Get the SAN notation for a move."""
        return self.board.san(move)

    def get_move_uci(self, move: chess.Move) -> str:
        """Get the UCI notation for a move."""
        return move.uci()

    def get_piece_name(self, symbol: str) -> str:
        """Get the name of a piece from its symbol."""
        names = {'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
        return names.get(symbol.upper(), 'unknown piece') 