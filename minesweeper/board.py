"""
================================================================================
Module:        minesweeper.board
Description:   Holds the board state for Minesweeper: the 10x10 grid of cells,
               random mine placement (with a guaranteed-safe first click),
               revealing and flagging cells, win detection, and rendering the
               board as text. Also converts between player coordinates ("A1")
               and zero-based grid indices.

Functions:     parse_coordinate(text)       -> (row, col)
               format_coordinate(row, col)  -> str
Classes:       Board
                 __init__(mine_count, rng=None)
                 in_bounds(row, col)        -> bool
                 neighbors(row, col)        -> iterator of (row, col)
                 place_mines(safe_row, safe_col) -> None
                 toggle_flag(row, col)      -> None
                 reveal(row, col)           -> bool (True if a mine was hit)
                 flags_remaining()          -> int
                 is_cleared()               -> bool
                 render(show_mines=False)   -> str

Inputs:        Mine count (10-20) and cell coordinates supplied by game.py
Outputs:       Updated board state, hit/win results, printable board string

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. The flood-fill reveal uses the
               standard iterative depth-first search technique (common
               algorithm, no specific source copied). Uses Python's
               standard-library random module
               (https://docs.python.org/3/library/random.html).
               Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

import random
from typing import Iterator, Optional

from . import config
from .cell import Cell


def parse_coordinate(text: str) -> tuple[int, int]:
    """Convert a label like 'A1' or 'j10' into zero-based (row, col).

    Inputs:  text (str) - column letter A-J followed by row number 1-10;
             case-insensitive, surrounding whitespace ignored.
    Outputs: (row, col) tuple of ints, each in range 0-9.
    Raises:  ValueError if the text is not a valid board coordinate.
    """
    # Sourced: Claude AI
    # Normalize so 'a1', ' A1 ', and 'A1' are treated the same.
    text = text.strip().upper()
    if len(text) < 2:
        raise ValueError(f"Invalid coordinate: {text!r}")

    # First character is the column letter; the rest is the row number.
    col_char, row_part = text[0], text[1:]
    if col_char not in config.COL_LABELS or not row_part.isdigit():
        raise ValueError(f"Invalid coordinate: {text!r}")

    # Convert from 1-based display numbers to 0-based list indices.
    row = int(row_part) - 1
    col = config.COL_LABELS.index(col_char)
    if not (0 <= row < config.ROWS):
        raise ValueError(f"Row out of range (1-{config.ROWS}): {text!r}")
    return row, col


def format_coordinate(row: int, col: int) -> str:
    """Convert zero-based (row, col) into a label like 'A1'.

    Inputs:  row (int) 0-9, col (int) 0-9
    Outputs: str such as 'A1' or 'J10'
    """
    # Sourced: Claude AI
    return f"{config.COL_LABELS[col]}{row + 1}"


class Board:
    """The Minesweeper grid and all operations that change or read it."""

    def __init__(self, mine_count: int, rng: Optional[random.Random] = None):
        """Create an empty, fully covered board.

        Inputs:  mine_count (int) - number of mines, must be 10-20.
                 rng (random.Random, optional) - random generator; pass a
                 seeded one to get repeatable boards in tests.
        Outputs: None (initializes the Board object).
        Raises:  ValueError if mine_count is outside the allowed range.
        """
        # Sourced: Claude AI
        # Enforce the required 10-20 mine range.
        if not (config.MIN_MINES <= mine_count <= config.MAX_MINES):
            raise ValueError(
                f"Mine count must be between {config.MIN_MINES} and {config.MAX_MINES}"
            )
        self.rows = config.ROWS
        self.cols = config.COLS
        self.mine_count = mine_count
        self.rng = rng or random.Random()

        # grid[row][col] -> Cell. Every cell starts covered with no flag.
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

        # Mines are placed lazily on the first reveal so that cell can be kept safe.
        self.mines_placed = False

    def in_bounds(self, row: int, col: int) -> bool:
        """Inputs: row, col (int). Outputs: True if the position is on the board."""
        # Sourced: Claude AI
        return 0 <= row < self.rows and 0 <= col < self.cols

    def neighbors(self, row: int, col: int) -> Iterator[tuple[int, int]]:
        """Yield the on-board positions surrounding (row, col).

        Inputs:  row, col (int) - center cell.
        Outputs: iterator of (row, col) tuples; up to 8 (fewer at edges/corners).
        """
        # Sourced: Claude AI
        # Check all 9 offsets in a 3x3 square, skipping (0, 0) (the cell itself)
        # and anything that falls off the edge of the board.
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr or dc) and self.in_bounds(row + dr, col + dc):
                    yield row + dr, col + dc

    def place_mines(self, safe_row: int, safe_col: int) -> None:
        """Randomly place mines, keeping the first-clicked cell (and optionally
        its neighbors) mine-free, then compute adjacency counts.

        Inputs:  safe_row, safe_col (int) - position of the player's first reveal.
        Outputs: None. Sets Cell.is_mine and Cell.adjacent_mines on the grid
                 and marks self.mines_placed True.
        """
        # Sourced: Claude AI
        # --- Step 1: build the set of cells that must stay mine-free ---
        safe = {(safe_row, safe_col)}
        if config.SAFE_NEIGHBORS_ON_FIRST_CLICK:
            safe.update(self.neighbors(safe_row, safe_col))

        # --- Step 2: list every other cell as a possible mine location ---
        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in safe
        ]

        # --- Step 3: pick mine_count distinct cells at random ---
        # random.sample chooses without replacement, so no duplicate mines.
        for r, c in self.rng.sample(candidates, self.mine_count):
            self.grid[r][c].is_mine = True

        # --- Step 4: store how many mines touch each cell ---
        # Booleans sum as 0/1, giving the neighbor mine count directly.
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].adjacent_mines = sum(
                    self.grid[nr][nc].is_mine for nr, nc in self.neighbors(r, c)
                )
        self.mines_placed = True

    def toggle_flag(self, row: int, col: int) -> None:
        """Flag or unflag a covered cell.

        Inputs:  row, col (int) - cell to toggle.
        Outputs: None. Revealed cells and off-board coordinates are ignored.
        """
        # Sourced: Claude AI
        # Ignore off-board coordinates (see the note in reveal() about negative
        # indices wrapping around to the far side of the grid).
        if not self.in_bounds(row, col):
            return
        cell = self.grid[row][col]
        if not cell.is_revealed:  # flags only make sense on covered cells
            cell.is_flagged = not cell.is_flagged

    def reveal(self, row: int, col: int) -> bool:
        """Uncover a cell, opening surrounding empty areas automatically.

        Inputs:  row, col (int) - cell the player chose to reveal.
        Outputs: bool - True if a mine was hit (game over), otherwise False.
                 Flagged, already revealed, and off-board coordinates are
                 ignored (returns False).
        """
        # Sourced: Claude AI
        # Reject coordinates outside the grid. Python's negative indexing would
        # silently wrap (grid[-1] is the last row), so an unchecked bad click
        # would quietly open the wrong cell instead of doing nothing.
        if not self.in_bounds(row, col):
            return False

        cell = self.grid[row][col]
        # Ignore clicks on cells that are already open or protected by a flag.
        # This is checked BEFORE mines are placed on purpose: clicking a flagged
        # cell is not a real reveal, so it must not anchor the guaranteed-safe
        # first-click zone on a cell the player never actually uncovers.
        if cell.is_revealed or cell.is_flagged:
            return False

        # First real reveal of the game: place mines now so this cell is safe.
        if not self.mines_placed:
            self.place_mines(row, col)
        # Stepped on a mine: uncover it and report the loss.
        if cell.is_mine:
            cell.is_revealed = True
            return True

        # Flood-fill outward from cells with no adjacent mines.
        # Sourced: Claude AI, standard iterative DFS using a stack (avoids
        # Python's recursion limit). A '0' cell reveals all its neighbors;
        # numbered cells are revealed but do not spread further.
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            current = self.grid[r][c]
            if current.is_revealed or current.is_flagged:
                continue  # already handled, or player flagged it
            current.is_revealed = True
            if current.adjacent_mines == 0:
                stack.extend(self.neighbors(r, c))
        return False

    def flags_remaining(self) -> int:
        """Outputs: int - mine count minus flags placed (can go negative)."""
        # Sourced: Claude AI
        flagged = sum(cell.is_flagged for row in self.grid for cell in row)
        return self.mine_count - flagged

    def is_cleared(self) -> bool:
        """True when every non-mine cell has been revealed.

        Outputs: bool - True means the player has won.
        """
        # Sourced: Claude AI
        # A board with no mines yet (no clicks) can never count as cleared.
        return self.mines_placed and all(
            cell.is_revealed or cell.is_mine for row in self.grid for cell in row
        )

    def render(self, show_mines: bool = False) -> str:
        """Build a text drawing of the board with A-J / 1-10 labels.

        Inputs:  show_mines (bool) - if True, draw all mines (game over view).
        Outputs: str - multi-line string ready to print.
        """
        # Sourced: Claude AI
        # Header row of column letters, indented to line up with the grid.
        header = "    " + " ".join(config.COL_LABELS[: self.cols])
        lines = [header]
        # One line per row: right-aligned row number, then each cell's symbol.
        for r in range(self.rows):
            symbols = " ".join(cell.symbol(show_mines) for cell in self.grid[r])
            lines.append(f"{r + 1:>2}  {symbols}")
        return "\n".join(lines)
