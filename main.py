"""
================================================================================
Module:        main
Description:   Entry point for the Minesweeper game. Run `python main.py` from
               the project root to start a game in the terminal.

Functions:     None (calls minesweeper.game.play)

Inputs:        None directly; the game reads keyboard input
Outputs:       None directly; the game prints to the terminal

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

from minesweeper.game import play

# Sourced: Claude AI
# Only start the game when this file is run directly, not when it is imported.
if __name__ == "__main__":
    play()
