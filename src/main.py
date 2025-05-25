import asyncio
import chess
from bot import ChessBot

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
    print_board(bot.get_board())

    while not bot.is_game_over():
        user_input = get_move_from_user(bot.get_board())
        match user_input:
            case "help":
                print("Getting hint...")
                hint = await bot.get_hint()
                if hint:
                    print(f"Hint: move a {piece_name_from_symbol(hint)}.")
                else:
                    print("Error getting hint.")
                continue
            case "play":
                print("Using best calculated move...")
                bot_move = await bot.get_best_move()  # Will use stored move if exists
                if bot_move:
                    print("Suggested move: ", bot.get_board().san(bot_move)) # SAN needs context
                else:
                    print("Could not get best move.")
                continue
            case "exit":
                print("Thanks for playing! Goodbye!")
                await bot.close()
                return
            case _:
                move_san = bot.get_board().san(user_input)
                move_uci = user_input.uci()
                bot.make_move(user_input)
                print(f"Your move: {move_san} (UCI: {move_uci})")
                print_board(bot.get_board())

        if bot.is_game_over():
            break

        print("Bot is thinking...")
        bot_move = await bot.get_best_move(force_recalculate=True)  # Force recalculation for bot's turn
        if bot_move:
            move_san = bot.get_board().san(bot_move)
            move_uci = bot_move.uci()
            bot.make_move(bot_move)
            print(f"Bot played: {move_san} (UCI: {move_uci})")
            print_board(bot.get_board())

    result = bot.get_game_result()
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