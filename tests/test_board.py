"""
================================================================================
Module:        tests.test_board
Description:   Unit tests for minesweeper.board. Verifies coordinate parsing,
               10x10 board dimensions, the required initial state (covered,
               unflagged, no mines), the 10-20 mine count limit, and that the
               first click (and its neighbors, if enabled) is never a mine.

Classes:       TestCoordinates  - parse_coordinate / format_coordinate tests
               TestBoardSetup   - Board construction and mine placement tests

Inputs:        None (uses fixed random seeds for repeatable boards)
Outputs:       unittest pass/fail results

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Uses Python's standard-library
               unittest framework (https://docs.python.org/3/library/unittest.html).
               Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-14
================================================================================
"""

import random
import unittest

from minesweeper import config
from minesweeper.board import Board, format_coordinate, parse_coordinate


# Sourced: Claude AI
class TestCoordinates(unittest.TestCase):
    """Tests for converting between 'A1' labels and (row, col) indices."""

    def test_parse_corners(self):
        # Top-left and bottom-right corners; lowercase input is accepted.
        self.assertEqual(parse_coordinate("A1"), (0, 0))
        self.assertEqual(parse_coordinate("j10"), (9, 9))

    def test_round_trip(self):
        # Parsing then formatting should return the original label.
        self.assertEqual(format_coordinate(*parse_coordinate("E7")), "E7")

    def test_invalid(self):
        # Empty, missing row, column past J, row 0, row 11, reversed, no digits.
        for bad in ("", "A", "K1", "A0", "A11", "1A", "AA"):
            with self.assertRaises(ValueError):
                parse_coordinate(bad)


# Sourced: Claude AI
class TestBoardSetup(unittest.TestCase):
    """Tests for the board's size, starting state, and mine placement rules."""

    def test_dimensions_and_initial_state(self):
        # Board must be 10x10 with every cell covered, unflagged, and mine-free
        # (mines are not placed until the first reveal).
        board = Board(10)
        self.assertEqual(len(board.grid), 10)
        self.assertTrue(all(len(row) == 10 for row in board.grid))
        for row in board.grid:
            for cell in row:
                self.assertFalse(cell.is_revealed)
                self.assertFalse(cell.is_flagged)
                self.assertFalse(cell.is_mine)
        self.assertFalse(board.mines_placed)

    def test_mine_count_bounds(self):
        # Just outside the range is rejected; the exact limits are accepted.
        for bad in (9, 21):
            with self.assertRaises(ValueError):
                Board(bad)
        Board(config.MIN_MINES)
        Board(config.MAX_MINES)

    def test_first_click_is_safe(self):
        # Try 50 different seeds with the maximum mine count, clicking a corner.
        for seed in range(50):
            board = Board(20, rng=random.Random(seed))
            board.place_mines(0, 0)
            # Exactly the requested number of mines was placed.
            self.assertEqual(sum(c.is_mine for row in board.grid for c in row), 20)
            # The clicked cell is safe...
            self.assertFalse(board.grid[0][0].is_mine)
            # ...and so are its neighbors when that option is enabled.
            if config.SAFE_NEIGHBORS_ON_FIRST_CLICK:
                for r, c in board.neighbors(0, 0):
                    self.assertFalse(board.grid[r][c].is_mine)

    def test_first_reveal_never_hits_mine(self):
        # Revealing on a fresh board must never report a mine hit.
        for seed in range(50):
            board = Board(20, rng=random.Random(seed))
            self.assertFalse(board.reveal(5, 5))


if __name__ == "__main__":
    unittest.main()
