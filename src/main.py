#!/bin/python

import asyncio
import chess
from bot import ChessBot

def print_welcome():
    print("Welcome to Chess TUI!")
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

def get_level():
    print("Select bot level (1-10, where 1 = easy, 10 = hard):")
    while True:
        try:
            level = int(input("Level: "))
            if 1 <= level <= 10:
                return level
            else:
                print("Enter a number between 1 and 10.")
        except ValueError:
            print("Enter a valid number.")

# Main game loop
async def main_loop(board: chess.Board, bot: ChessBot) -> None:
    while True:
        command = input("Enter your move (e.g., 'e4', 'Nf3'), or ask for 'help', 'play', or 'exit': ").strip()
        match command:
            case "help":
                print("Getting hint...")
                hint = await bot.get_hint(board)
                if hint:
                    print(f"Hint: move a {hint}.")
                else:
                    print("Error getting hint.")
                continue
            case "play":
                print("Using best calculated move...")
                bot_move = await bot.get_play(board)  # Will use stored move if exists
                if bot_move:
                    print("Suggested move: ", bot_move)
                else:
                    print("Could not get best move.")
                continue
            case "exit":
                print("Thanks for playing! Goodbye!")
                await bot.close()
                return
            case _:
                try:
                    move = board.parse_san(command)
                    board.push_san(command)
                except chess.AmbiguousMoveError:
                    print("Ambiguous move! Be more specific (e.g., 'Rae1' for rook from a-file, 'Rhe1' for rook from h-file)")
                    continue
                except chess.IllegalMoveError:
                    print("Illegal move! Try again.")
                    continue
                except chess.InvalidMoveError:
                    print("Invalid move format! Try again.")
                    continue
                
                print(f"Your move: {move}")
                print(board)

        if board.is_game_over():
            print("Game over! You won")
            break

        print("Bot is thinking...")
        bot_move = await bot.get_best_move(board)
        if bot_move:
            board.push(bot_move)
            print(f"Bot played: {bot_move}")
            print(board)
        if board.is_game_over():
            print("Game over! Bot won")
            break
        print("Your turn!")

async def play_game():
    # Set up
    level = get_level()
    bot = ChessBot(level=level, engine_path="stockfish/stockfish-ubuntu-x86-64-avx2")
    board = chess.Board()
    
    if not await bot.initialize():
        print("Failed to initialize chess engine. Exiting...")
        return

    print_welcome()
    print(board)

    await main_loop(board, bot)
        
    await bot.close()

if __name__ == "__main__":
    asyncio.run(play_game())
