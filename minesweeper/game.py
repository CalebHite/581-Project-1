"""
================================================================================
Module:        minesweeper.game
Description:   Interactive terminal front end for Minesweeper. Asks the player
               for a mine count, then repeatedly draws the board, reads a
               command, and applies it until the player wins, loses, or quits.

Functions:     prompt_mine_count() -> int
               play()              -> None

Inputs:        Keyboard input from the player:
                 - mine count (10-20)
                 - commands: 'r <cell>' reveal, 'f <cell>' flag, 'q' quit
Outputs:       Board drawings and status messages printed to the terminal

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Reviewed by the author.

Author:        Caleb Hite & Kai Barnhart
Created:       2026-09-14
================================================================================
"""

from . import config
from .board import Board, parse_coordinate


def prompt_mine_count() -> int:
    """Ask the player how many mines to use, repeating until the answer is valid.

    Inputs:  Keyboard input (whole number).
    Outputs: int - mine count between config.MIN_MINES and config.MAX_MINES.
    """
    # Sourced: Claude AI
    # Loop until the input is a whole number inside the allowed range.
    while True:
        raw = input(f"Number of mines ({config.MIN_MINES}-{config.MAX_MINES}): ").strip()
        if raw.isdigit() and config.MIN_MINES <= int(raw) <= config.MAX_MINES:
            return int(raw)
        print(f"Please enter a whole number from {config.MIN_MINES} to {config.MAX_MINES}.")


def play() -> None:
    """Run one full game of Minesweeper in the terminal.

    Inputs:  Keyboard commands from the player (see module prologue).
    Outputs: None. Prints the board each turn and a final win/loss message.
    """
    # Sourced: Claude AI
    # --- Setup: create a covered, unflagged board (mines placed on first reveal) ---
    board = Board(prompt_mine_count())
    print("Commands: 'r A1' to reveal, 'f A1' to flag/unflag, 'q' to quit.")

    # --- Main game loop: draw, read command, update ---
    while True:
        print()
        print(board.render())
        # Status indicator and remaining mine count, both required by the
        # project specification. Inside this loop the game is always "Playing";
        # the win and loss branches below print the final status.
        print(f"Status: Playing   Mines remaining: {board.flags_remaining()}")

        # Split input into [command, coordinate]; ignore blank lines.
        parts = input("> ").strip().split()
        if not parts:
            continue

        # Quit command.
        if parts[0].lower() == "q":
            print("Goodbye!")
            return

        # Anything other than 'r <cell>' or 'f <cell>' is a usage error.
        if len(parts) != 2 or parts[0].lower() not in ("r", "f"):
            print("Usage: r <cell> | f <cell> | q")
            continue

        # Convert 'A1'-style text to grid indices; report bad coordinates.
        try:
            row, col = parse_coordinate(parts[1])
        except ValueError as exc:
            print(exc)
            continue

        # Flag command: toggle and go back to the top of the loop.
        if parts[0].lower() == "f":
            board.toggle_flag(row, col)
            continue

        # Reveal command: check for a loss first, then a win.
        if board.reveal(row, col):
            print()
            print(board.render(show_mines=True))
            print("Status: Game Over: Loss - you uncovered a mine.")
            return
        if board.is_cleared():
            print()
            print(board.render(show_mines=True))
            print("Status: Victory - you cleared every safe cell!")
            return
