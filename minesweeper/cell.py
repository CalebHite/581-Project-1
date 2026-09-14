"""
================================================================================
Module:        minesweeper.cell
Description:   Defines the Cell data class, which stores the state of a single
               square on the Minesweeper board and knows how to draw itself as
               a single character for the terminal display.

Classes:       Cell
                 Attributes:
                   is_mine        (bool) - True if this cell contains a mine
                   is_revealed    (bool) - True once the player uncovers it
                   is_flagged     (bool) - True if the player marked it
                   adjacent_mines (int)  - count of mines in the 8 neighbors
                 Methods:
                   symbol(show_mines=False) -> str

Inputs:        Cell state is set by minesweeper.board.Board
Outputs:       Cell objects; one-character display symbols

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Uses Python's standard-library
               dataclasses module (https://docs.python.org/3/library/dataclasses.html).
               Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

from dataclasses import dataclass  # auto-generates __init__/__repr__/__eq__


# Sourced: Claude AI
@dataclass
class Cell:
    """State of one board square. Defaults describe the required initial
    state: no mine, covered, and unflagged."""

    is_mine: bool = False
    is_revealed: bool = False  # all cells start covered
    is_flagged: bool = False  # all cells start unflagged
    adjacent_mines: int = 0  # filled in by Board.place_mines()

    def symbol(self, show_mines: bool = False) -> str:
        """Return the character used to draw this cell in the terminal.

        Inputs:  show_mines (bool) - if True, covered mines are drawn as '*'
                 (used to show the whole board at game over).
        Outputs: str - one of 'F' (flag), '#' (covered), '*' (mine),
                 '.' (revealed, no adjacent mines), or '1'-'8' (mine count).
        """
        # Sourced: Claude AI
        # A flag is only visible while the cell is still covered.
        if self.is_flagged and not self.is_revealed:
            return "F"
        # Covered cells hide their contents unless the game is revealing mines.
        if not self.is_revealed:
            return "*" if (show_mines and self.is_mine) else "#"
        # Revealed mine (the one the player stepped on).
        if self.is_mine:
            return "*"
        # Revealed safe cell: show its neighbor mine count, or '.' for zero.
        return str(self.adjacent_mines) if self.adjacent_mines else "."
