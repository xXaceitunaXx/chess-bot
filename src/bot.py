import chess
import chess.engine
import asyncio
from pathlib import Path
from typing import Optional

class ChessBot:
    def __init__(self, engine_path: str = "stockfish/stockfish-windows-x86-64-avx2.exe", level: float = 2.0):
        self.engine_path = engine_path
        self.engine = None
        self.level = level  # tiempo de cálculo en segundos
        self.last_best_move = None  # almacena la última mejor jugada calculada

    async def initialize(self) -> bool:
        """Initialize the chess engine."""
        try:
            transport, engine = await chess.engine.popen_uci(self.engine_path)
            self.engine = engine
            return True
        except Exception as e:
            print(f"Error initializing engine: {e}")
            return False

    async def get_best_move(self, board: chess.Board, time_limit: Optional[float] = None, force_recalculate: bool = False) -> Optional[chess.Move]:
        """Get the best move from the current position."""
        if not self.engine:
            return None
        
        # Si ya tenemos una jugada calculada y no forzamos recálculo, la devolvemos
        if not force_recalculate and self.last_best_move:
            return self.last_best_move

        if time_limit is None:
            time_limit = self.level
        result = await self.engine.play(
            board,
            chess.engine.Limit(time=5.0, depth=20)  # Usamos un tiempo fijo de 5 segundos y profundidad mínima de 20
        )
        self.last_best_move = result.move  # guardamos la jugada calculada
        return result.move

    async def get_hint(self, board: chess.Board) -> Optional[str]:
        """Get a hint for the best move (piece type only)."""
        best_move = await self.get_best_move(board)  # esto ya guarda la jugada en last_best_move
        if best_move:
            piece = board.piece_at(best_move.from_square)
            assert piece is not None
            return piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
        return None

    async def close(self):
        """Close the engine connection."""
        if self.engine:
            await self.engine.quit()
