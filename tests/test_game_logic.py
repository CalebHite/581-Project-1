"""
================================================================================
Module:        tests.test_game_logic
Description:   Unit tests for the gameplay rules in minesweeper.board that go
               beyond board setup: flagging, flags blocking reveals, recursive
               (flood-fill) uncovering, adjacency counts, win and loss
               detection, the remaining-mine counter, off-board input, and a
               randomized stress test that plays many games and checks the
               board's invariants after every move.

Classes:       TestFlagging       - flag toggling and the remaining-mine count
               TestRevealing      - flood fill, adjacency counts, first-click
                                    safety when the first click is flagged
               TestGameConclusion - win and loss detection
               TestRobustness     - off-board input and randomized stress test

Inputs:        None (uses fixed random seeds so every board is reproducible)
Outputs:       unittest pass/fail results

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Uses Python's standard-library
               unittest (https://docs.python.org/3/library/unittest.html) and
               random (https://docs.python.org/3/library/random.html) modules.
               Reviewed by the author.

Author:        Caleb Hite
Created:       2026-09-20
================================================================================
"""

import random
import unittest

from minesweeper import config
from minesweeper.board import Board


# Sourced: Claude AI
def make_board(seed: int, mines: int = 10) -> Board:
    """Build a board with a fixed seed so tests are repeatable.

    Inputs:  seed (int) - random seed; mines (int) - mine count 10-20.
    Outputs: Board - a fresh, fully covered board.
    """
    return Board(mines, rng=random.Random(seed))


# Sourced: Claude AI
def first_mine(board: Board) -> tuple[int, int]:
    """Find any mine on a board whose mines have already been placed.

    Inputs:  board (Board) - a board with mines_placed True.
    Outputs: (row, col) of the first mine found, scanning top-left to
             bottom-right.
    """
    for r in range(board.rows):
        for c in range(board.cols):
            if board.grid[r][c].is_mine:
                return r, c
    raise AssertionError("board has no mines")  # unreachable for 10-20 mines


# Sourced: Claude AI
class TestFlagging(unittest.TestCase):
    """Flags: toggling, protecting covered cells, and the remaining counter."""

    def test_toggle_on_and_off(self):
        # A flag goes on with one call and comes off with a second.
        board = make_board(1)
        board.toggle_flag(3, 4)
        self.assertTrue(board.grid[3][4].is_flagged)
        board.toggle_flag(3, 4)
        self.assertFalse(board.grid[3][4].is_flagged)

    def test_flag_blocks_reveal(self):
        # Requirement: flagged cells cannot be uncovered until unflagged.
        board = make_board(2)
        board.reveal(5, 5)  # open the board so mines exist
        # Find a cell that is still covered after the first reveal.
        target = next(
            (r, c)
            for r in range(10)
            for c in range(10)
            if not board.grid[r][c].is_revealed
        )
        board.toggle_flag(*target)
        self.assertFalse(board.reveal(*target))  # no mine hit reported
        self.assertFalse(board.grid[target[0]][target[1]].is_revealed)
        # Unflagging makes the same cell uncoverable again.
        board.toggle_flag(*target)
        board.reveal(*target)
        cell = board.grid[target[0]][target[1]]
        self.assertTrue(cell.is_revealed or cell.is_mine)

    def test_cannot_flag_revealed_cell(self):
        # Flags only make sense on covered cells.
        board = make_board(3)
        board.reveal(5, 5)
        board.toggle_flag(5, 5)
        self.assertFalse(board.grid[5][5].is_flagged)

    def test_flags_remaining_counts_down_and_back_up(self):
        # Requirement: display total mines minus flags placed.
        board = make_board(4, mines=15)
        self.assertEqual(board.flags_remaining(), 15)
        board.toggle_flag(0, 0)
        board.toggle_flag(0, 1)
        self.assertEqual(board.flags_remaining(), 13)
        board.toggle_flag(0, 0)  # remove one flag
        self.assertEqual(board.flags_remaining(), 14)

    def test_flags_remaining_may_go_negative(self):
        # Over-flagging is allowed and simply shows a negative count, matching
        # the classic game. This is documented behavior, not a bug.
        board = make_board(5, mines=10)
        for i in range(12):
            board.toggle_flag(i // 10, i % 10)
        self.assertEqual(board.flags_remaining(), -2)


# Sourced: Claude AI
class TestRevealing(unittest.TestCase):
    """Uncovering cells: adjacency counts, flood fill, and first-click safety."""

    def test_adjacent_counts_match_actual_mines(self):
        # Every cell's stored number must equal the mines around it.
        for seed in range(20):
            board = make_board(seed, mines=20)
            board.place_mines(4, 4)
            for r in range(10):
                for c in range(10):
                    expected = sum(
                        board.grid[nr][nc].is_mine for nr, nc in board.neighbors(r, c)
                    )
                    self.assertEqual(board.grid[r][c].adjacent_mines, expected)
                    # Requirement: the number shown is always 0-8.
                    self.assertTrue(0 <= expected <= 8)

    def test_zero_cells_reveal_their_neighbors(self):
        # Requirement: cells with zero adjacent mines recursively uncover their
        # neighbors. After any reveal, no revealed '0' cell may still have a
        # covered, unflagged neighbor.
        for seed in range(20):
            board = make_board(seed, mines=10)
            board.reveal(5, 5)
            for r in range(10):
                for c in range(10):
                    cell = board.grid[r][c]
                    if cell.is_revealed and cell.adjacent_mines == 0:
                        for nr, nc in board.neighbors(r, c):
                            self.assertTrue(board.grid[nr][nc].is_revealed)

    def test_flood_fill_never_reveals_a_mine(self):
        # The recursive uncovering must stop at numbered cells, so it can never
        # open a mine by accident.
        for seed in range(30):
            board = make_board(seed, mines=20)
            board.reveal(5, 5)
            for row in board.grid:
                for cell in row:
                    if cell.is_mine:
                        self.assertFalse(cell.is_revealed)

    def test_first_click_on_flagged_cell_does_not_start_game(self):
        # Regression test: clicking a flagged cell is not a real reveal, so it
        # must not place mines. Otherwise the guaranteed-safe zone would be
        # anchored on a cell the player never actually uncovers.
        board = make_board(6)
        board.toggle_flag(0, 0)
        self.assertFalse(board.reveal(0, 0))
        self.assertFalse(board.mines_placed)
        # A real reveal elsewhere still gets its own safe first click.
        self.assertFalse(board.reveal(7, 7))
        self.assertTrue(board.mines_placed)
        self.assertFalse(board.grid[7][7].is_mine)

    def test_revealing_same_cell_twice_is_harmless(self):
        # Repeated clicks on an open cell must not change anything.
        board = make_board(7)
        board.reveal(5, 5)
        revealed_before = sum(c.is_revealed for row in board.grid for c in row)
        self.assertFalse(board.reveal(5, 5))
        revealed_after = sum(c.is_revealed for row in board.grid for c in row)
        self.assertEqual(revealed_before, revealed_after)


# Sourced: Claude AI
class TestGameConclusion(unittest.TestCase):
    """Win and loss detection."""

    def test_revealing_a_mine_is_a_loss(self):
        # Requirement: uncovering a mine ends the game.
        board = make_board(8, mines=20)
        board.place_mines(0, 0)  # place mines without revealing anything
        mine_row, mine_col = first_mine(board)
        self.assertTrue(board.reveal(mine_row, mine_col))
        self.assertTrue(board.grid[mine_row][mine_col].is_revealed)

    def test_board_is_not_cleared_before_play(self):
        # A fresh board with no mines placed can never count as a win.
        board = make_board(9)
        self.assertFalse(board.is_cleared())

    def test_win_after_revealing_every_safe_cell(self):
        # Requirement: win by uncovering all non-mine cells.
        for seed in range(10):
            board = make_board(seed, mines=15)
            board.reveal(5, 5)
            self.assertFalse(board.is_cleared())  # not won on the first click
            for r in range(10):
                for c in range(10):
                    if not board.grid[r][c].is_mine:
                        self.assertFalse(board.reveal(r, c))
            self.assertTrue(board.is_cleared())

    def test_win_does_not_require_flagging_mines(self):
        # Flags are a player aid only; the win condition depends on revealed
        # safe cells, not on where flags were placed.
        board = make_board(11, mines=10)
        board.reveal(5, 5)
        for r in range(10):
            for c in range(10):
                if not board.grid[r][c].is_mine:
                    board.reveal(r, c)
        self.assertTrue(board.is_cleared())
        self.assertEqual(board.flags_remaining(), 10)  # no flags were used


# Sourced: Claude AI
class TestRobustness(unittest.TestCase):
    """Bad input and a randomized stress test, per the stress-testing criterion."""

    def test_off_board_coordinates_are_ignored(self):
        # Negative and too-large indices must do nothing rather than crash or
        # wrap around to the opposite edge (Python's grid[-1] is the last row).
        board = make_board(12)
        board.reveal(5, 5)
        snapshot = [
            (c.is_revealed, c.is_flagged) for row in board.grid for c in row
        ]
        for r, c in ((-1, 0), (0, -1), (10, 0), (0, 10), (99, 99), (-5, -5)):
            self.assertFalse(board.reveal(r, c))
            board.toggle_flag(r, c)
        after = [(c.is_revealed, c.is_flagged) for row in board.grid for c in row]
        self.assertEqual(snapshot, after)

    def test_render_shape(self):
        # The text board is one header line plus one line per row.
        board = make_board(13)
        lines = board.render().splitlines()
        self.assertEqual(len(lines), config.ROWS + 1)
        for label in config.COL_LABELS:
            self.assertIn(label, lines[0])

    def test_random_play_never_breaks_invariants(self):
        # Stress test: play 40 games of 200 random moves each, mixing reveals,
        # flags, and deliberately invalid coordinates. After every move the
        # board must still satisfy its invariants and must never raise.
        rng = random.Random(1234)
        for seed in range(40):
            board = make_board(seed, mines=rng.randint(config.MIN_MINES, config.MAX_MINES))
            for _ in range(200):
                # Occasionally feed an off-board coordinate to the board.
                if rng.random() < 0.1:
                    r, c = rng.randint(-3, 13), rng.randint(-3, 13)
                else:
                    r, c = rng.randrange(10), rng.randrange(10)

                if rng.random() < 0.3:
                    board.toggle_flag(r, c)
                else:
                    if board.reveal(r, c):
                        break  # hit a mine; this game is over

                # Invariant 1: a cell is never both revealed and flagged.
                for row in board.grid:
                    for cell in row:
                        self.assertFalse(cell.is_revealed and cell.is_flagged)
                # Invariant 2: the counter always matches the flags on the board.
                flagged = sum(c.is_flagged for row in board.grid for c in row)
                self.assertEqual(board.flags_remaining(), board.mine_count - flagged)
            # Invariant 3: the requested number of mines is always present once
            # the game has started.
            if board.mines_placed:
                mines = sum(c.is_mine for row in board.grid for c in row)
                self.assertEqual(mines, board.mine_count)


if __name__ == "__main__":
    unittest.main()
