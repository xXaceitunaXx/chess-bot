import chess
import chess.engine
from typing import Optional


def name_from_piece(piece: chess.Piece) -> str:
        names = {
            chess.PAWN: "pawn",
            chess.KNIGHT: "knight",
            chess.BISHOP: "bishop",
            chess.ROOK: "rook",
            chess.QUEEN: "queen",
            chess.KING: "king"
        }
        return names.get(piece.piece_type, "unknown")
    
class ChessBot:
    def __init__(self, engine_path: str, level: float = 2.0):
        self.engine_path = engine_path
        self.engine = None
        self.level = 0.1 + (level - 1) * (5.0 - 0.1) / 9  # tiempo de cálculo en segundos
        self.last_best_move = None  # almacena la última mejor jugada calculada

    async def initialize(self) -> bool:
        try:
            _, engine = await chess.engine.popen_uci(self.engine_path)
            self.engine = engine
            return True
        except Exception as e:
            print(f"Error initializing engine: {e}")
            return False

    async def get_best_move(self, board: chess.Board, time_limit: Optional[float] = None, user_request: bool = False) -> Optional[chess.Move]:
        if not self.engine:
            return None

        if time_limit is None:
            time_limit = self.level
        result = await self.engine.play(
            board,
            chess.engine.Limit(time=time_limit)
        )
        
        self.last_best_move = result.move if user_request else None
        
        return result.move

    async def get_hint(self, board: chess.Board) -> Optional[chess.Piece]:
        if self.last_best_move:
            return name_from_piece(board.piece_at(self.last_best_move.from_square))
        
        best_move = await self.get_best_move(board, time_limit=5.0, user_request=True)  # esto ya guarda la jugada en last_best_move
        if best_move:
            piece = board.piece_at(best_move.from_square)
            return name_from_piece(piece)
        return None
    
    async def get_play(self, board: chess.Board) -> Optional[chess.Move]:
        if self.last_best_move:
            return self.last_best_move
        return await self.get_best_move(board, time_limit=5.0 ,user_request=True)

    async def close(self):
        if self.engine:
            await self.engine.quit()
