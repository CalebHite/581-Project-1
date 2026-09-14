"""
================================================================================
Module:        minesweeper.config
Description:   Central configuration constants for the Minesweeper game. Every
               other module reads board size, column labels, mine limits, and
               the first-click safety rule from here, so game rules can be
               changed in one place.

Contents:      Constants only (no functions or classes)
                 ROWS, COLS                     - board dimensions (10x10)
                 COL_LABELS                     - column letters A-J
                 MIN_MINES, MAX_MINES           - allowed mine count range
                 SAFE_NEIGHBORS_ON_FIRST_CLICK  - first-click safety option

Inputs:        None
Outputs:       Module-level constants imported by board.py, game.py, and tests

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code, prompted with the project's
               board and mine configuration requirements. Reviewed by the
               author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

# --- Board configuration (Sourced: Claude AI, from project requirements) ---
ROWS = 10               # number of rows, labeled 1-10 when displayed
COLS = 10               # number of columns, labeled A-J when displayed
COL_LABELS = "ABCDEFGHIJ"  # index 0 -> 'A', index 9 -> 'J'

# --- Mine configuration (Sourced: Claude AI, from project requirements) ---
MIN_MINES = 10          # fewest mines a player may request
MAX_MINES = 20          # most mines a player may request

# --- First-click safety (Sourced: Claude AI) ---
# When True, the first revealed cell AND its neighbors are guaranteed mine-free.
# When False, only the first revealed cell itself is guaranteed safe.
# Worst case safe zone is 9 cells, leaving 91 cells for at most 20 mines.
SAFE_NEIGHBORS_ON_FIRST_CLICK = True
