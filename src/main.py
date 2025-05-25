import asyncio
import chess
from bot import ChessBot
from board import Board

def print_board(board):
    """Print the current board state."""
    print("\n" + str(board) + "\n")

def get_move_from_user(board):
    """Get a move from the user in SAN format."""
    while True:
        move_san = input("Enter your move (e.g., 'e4', 'Nf3'), or ask for 'help', 'play', or 'exit': ").strip()
        if move_san.lower() in ("help", "play", "exit"):
            return move_san.lower()
        try:
            move = board.parse_san(move_san)
            return move
        except chess.AmbiguousMoveError:
            print("Ambiguous move! Be more specific (e.g., 'Rae1' for rook from a-file, 'Rhe1' for rook from h-file)")
        except chess.IllegalMoveError:
            print("Illegal move! Try again.")
        except chess.InvalidMoveError:
            print("Invalid move format! Try again.")

def piece_name_from_symbol(symbol):
    names = {'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
    return names.get(symbol.upper(), 'unknown piece')

async def play_game():
    """Main game loop."""
    print("Select bot level (1-10, where 1 = easy, 10 = hard):")
    while True:
        try:
            level = int(input("Level: "))
            if 1 <= level <= 10:
                break
            else:
                print("Enter a number between 1 and 10.")
        except ValueError:
            print("Enter a valid number.")
    # Map level to calculation time (0.1s to 5s)
    time_per_move = 0.1 + (level - 1) * (5.0 - 0.1) / 9
    bot = ChessBot(level=time_per_move)
    board = Board()
    
    if not await bot.initialize():
        print("Failed to initialize chess engine. Exiting...")
        return

    print("Welcome to Chess CLI!")
    print("Commands:")
    print("  - 'help': get a hint")
    print("  - 'play': let the bot play for you")
    print("  - 'exit': quit the game")
    print("\nMove notation examples (SAN):")
    print("  - Basic moves: e4, Nf3, Bc4")
    print("  - Captures: Bxe5, exd5")
    print("  - Check: Qh5+")
    print("  - Checkmate: Qxf7#")
    print("  - Castling: O-O (kingside) or O-O-O (queenside)")
    print("  - Promotion: e8=Q")
    print("  - Disambiguation: Rae1 (rook from a-file), Nbd7 (knight from b-file)")
    print("    Use file (a-h) or rank (1-8) to specify which piece to move")
    board.print_board()

    while not board.is_game_over():
        move, command = board.get_move_from_user()
        match command:
            case "help":
                print("Getting hint...")
                hint = await bot.get_hint(board.get_board())
                if hint:
                    print(f"Hint: move a {board.get_piece_name(hint)}.")
                else:
                    print("Error getting hint.")
                continue
            case "play":
                print("Using best calculated move...")
                bot_move = await bot.get_best_move(board.get_board())  # Will use stored move if exists
                if bot_move:
                    print("Suggested move: ", board.get_move_san(bot_move))
                else:
                    print("Could not get best move.")
                continue
            case "exit":
                print("Thanks for playing! Goodbye!")
                await bot.close()
                return
            case _:
                if move:
                    move_san = board.get_move_san(move)
                    move_uci = board.get_move_uci(move)
                    board.make_move(move)
                    print(f"Your move: {move_san} (UCI: {move_uci})")
                    board.print_board()

        if board.is_game_over():
            break

        print("Bot is thinking...")
        bot_move = await bot.get_best_move(board.get_board(), force_recalculate=True)  # Force recalculation for bot's turn
        if bot_move:
            move_san = board.get_move_san(bot_move)
            move_uci = board.get_move_uci(bot_move)
            board.make_move(bot_move)
            print(f"Bot played: {move_san} (UCI: {move_uci})")
            board.print_board()

    result = board.get_game_result()
    if result:
        if result.winner == chess.WHITE:
            print("You won!")
        elif result.winner == chess.BLACK:
            print("Bot won!")
        else:
            print("Game ended in a draw!")
    await bot.close()

if __name__ == "__main__":
    asyncio.run(play_game()) 