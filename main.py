"""
================================================================================
Module:        main
Description:   Entry point for the Minesweeper game. Run `python main.py` from
               the project root to open the clickable game window, or
               `python main.py --text` to play the original terminal version.
               If Tkinter is missing from the Python installation, the game
               explains how to fix it and falls back to the terminal version.

Functions:     main() -> None

Inputs:        One optional command-line flag: --text (or -t) for terminal play
Outputs:       A game window, or terminal output in text mode

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

import sys


def main() -> None:
    """Start the graphical game, or the terminal game if --text is given.

    Inputs:  Command-line arguments from sys.argv.
    Outputs: None. Runs until the player quits or closes the window.
    """
    # Sourced: Claude AI
    # Text mode is opt-in; the clickable window is the default experience.
    if any(arg in ("--text", "-t") for arg in sys.argv[1:]):
        from minesweeper.game import play

        play()
        return

    # Tkinter ships with most Python builds but can be missing (for example a
    # Homebrew Python without python-tk). Explain the fix instead of crashing.
    try:
        from minesweeper.gui import run
    except ImportError:
        print("Tkinter is not available in this Python installation.")
        print("Install it (macOS: 'brew install python-tk', Ubuntu: "
              "'sudo apt install python3-tk') or run 'python main.py --text'.")
        print("Falling back to the terminal version.\n")
        from minesweeper.game import play

        play()
        return

    run()


# Sourced: Claude AI
# Only start the game when this file is run directly, not when it is imported.
if __name__ == "__main__":
    main()
