"""
================================================================================
Module:        minesweeper.gui
Description:   Creates the GUI for users to play the minesweeper game. Uses the tkinter library.
Functions:     run() -> None
Classes:       MinesweeperGUI
                 __init__(root)                  - build all widgets
                 new_game()                      - reset board and display
                 on_left_click(row, col)         - reveal a cell
                 on_right_click(row, col)        - toggle a flag
                 on_double_click(row, col)       - chord around a number
                 refresh()                       - redraw grid from board state
                 finish(won)                     - end the game and reveal mines

Inputs:        Mouse clicks on the grid, mine-count selection, and New Game
               presses from the player
Outputs:       An on-screen game window; no console output

External Sources:
               Generated with the assistance of Claude (Anthropic, model
               Claude Opus 5) via Claude Code. Uses Python's standard-library
               tkinter module (https://docs.python.org/3/library/tkinter.html).
               The number colors follow the classic Minesweeper palette.
               Reviewed by the author.

Author:        Will Calhoun
Created:       2026-09-14
================================================================================
"""

import tkinter as tk
from tkinter import font as tkfont

from . import config
from .board import Board

# --- Appearance constants (Sourced: Claude AI, classic Minesweeper look) ---
COVERED_COLOR = "#bdbdbd"   # raised, unclicked cell
REVEALED_COLOR = "#e0e0e0"  # opened cell
MINE_COLOR = "#ff5252"      # the mine the player stepped on
PANEL_COLOR = "#d4d4d4"     # window background
CELL_SIZE = 3               # cell width in text units

# Each adjacent-mine count gets its own color, as in the original game.
NUMBER_COLORS = {
    1: "#1976d2",
    2: "#388e3c",
    3: "#d32f2f",
    4: "#7b1fa2",
    5: "#bf360c",
    6: "#0097a7",
    7: "#212121",
    8: "#616161",
}


class MinesweeperGUI:
    """Window that draws a Board and turns mouse clicks into board moves."""

    def __init__(self, root: tk.Tk):
        """Build the control bar, the clickable grid, and the status bar.

        Inputs:  root (tk.Tk) - the top-level window to fill.
        Outputs: None. Leaves a ready-to-play game on screen.
        """
        # Sourced: Claude AI
        self.root = root
        self.root.title("Minesweeper")
        self.root.configure(bg=PANEL_COLOR)
        self.root.resizable(False, False)

        # Game state that is rebuilt by new_game().
        self.board = Board(config.MIN_MINES)
        self.game_over = False
        self.seconds = 0
        self.timer_job = None  # id of the pending after() callback, if any

        # Fonts: one bold face for cells, one plain face for the bars.
        self.cell_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.text_font = tkfont.Font(family="Helvetica", size=12)

        self._build_control_bar()
        self._build_grid()
        self._build_status_bar()
        self.new_game()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_control_bar(self) -> None:
        """Create the mine-count chooser and the New Game button.

        Inputs:  None (uses self.root).
        Outputs: None. Stores the mine-count variable on self.
        """
        # Sourced: Claude AI
        bar = tk.Frame(self.root, bg=PANEL_COLOR, padx=10, pady=8)
        bar.pack(fill="x")

        tk.Label(bar, text="Mines:", bg=PANEL_COLOR, font=self.text_font).pack(side="left")

        # Spinbox limits the player to the required 10-20 mines, so an invalid
        # count can never reach Board().
        self.mine_var = tk.StringVar(value=str(config.MIN_MINES))
        tk.Spinbox(
            bar,
            from_=config.MIN_MINES,
            to=config.MAX_MINES,
            width=4,
            justify="center",
            state="readonly",
            textvariable=self.mine_var,
            font=self.text_font,
        ).pack(side="left", padx=(6, 12))

        tk.Button(
            bar, text="New Game", font=self.text_font, command=self.new_game
        ).pack(side="left")

        # Status indicator
        self.status_label = tk.Label(
            bar, text="Playing", bg=PANEL_COLOR, font=self.text_font, fg="#212121"
        )
        self.status_label.pack(side="right")

    def _build_grid(self) -> None:
        """Create the A-J / 1-10 labels and the clickable cell widgets.

        Inputs:  None (board size comes from config).
        Outputs: None. Fills self.cells with a grid of tk.Label widgets.
        """
        # Sourced: Claude AI
        frame = tk.Frame(self.root, bg=PANEL_COLOR, padx=10, pady=4)
        frame.pack()

        # Column letters across the top; row 0 of the layout grid.
        for c in range(config.COLS):
            tk.Label(
                frame,
                text=config.COL_LABELS[c],
                bg=PANEL_COLOR,
                font=self.text_font,
                width=CELL_SIZE,
            ).grid(row=0, column=c + 1)

        # One Label per cell. Labels (rather than Buttons) are used because
        # their background color renders the same on every platform.
        self.cells = []
        for r in range(config.ROWS):
            tk.Label(
                frame,
                text=str(r + 1),
                bg=PANEL_COLOR,
                font=self.text_font,
                width=2,
                anchor="e",
            ).grid(row=r + 1, column=0, padx=(0, 4))

            row_widgets = []
            for c in range(config.COLS):
                label = tk.Label(
                    frame,
                    width=CELL_SIZE,
                    font=self.cell_font,
                    bg=COVERED_COLOR,
                    relief="raised",
                    borderwidth=2,
                )
                label.grid(row=r + 1, column=c + 1, padx=1, pady=1)

                # Default arguments capture this cell's coordinates so every
                # widget reports its own position instead of the loop's last one.
                label.bind("<Button-1>", lambda _e, r=r, c=c: self.on_left_click(r, c))
                label.bind("<Double-Button-1>", lambda _e, r=r, c=c: self.on_double_click(r, c))
                # Right-click differs by platform: Button-3 on Windows/Linux,
                # Button-2 or Control-click on macOS. Bind all three.
                for sequence in ("<Button-2>", "<Button-3>", "<Control-Button-1>"):
                    label.bind(sequence, lambda _e, r=r, c=c: self.on_right_click(r, c))
                row_widgets.append(label)
            self.cells.append(row_widgets)

    def _build_status_bar(self) -> None:
        """Create the flags-remaining counter, timer, and help text.

        Inputs:  None.
        Outputs: None. Stores the status labels on self.
        """
        # Sourced: Claude AI
        bar = tk.Frame(self.root, bg=PANEL_COLOR, padx=10, pady=8)
        bar.pack(fill="x")

        self.flags_label = tk.Label(bar, bg=PANEL_COLOR, font=self.text_font)
        self.flags_label.pack(side="left")

        self.timer_label = tk.Label(bar, bg=PANEL_COLOR, font=self.text_font)
        self.timer_label.pack(side="right")

        tk.Label(
            self.root,
            text="Left-click reveals \u00b7 Right-click flags \u00b7 Double-click a number to clear around it",
            bg=PANEL_COLOR,
            fg="#555555",
            font=tkfont.Font(family="Helvetica", size=10),
            pady=6,
        ).pack()

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def new_game(self) -> None:
        """Throw away the current board and start a fresh game.

        Inputs:  None (reads the mine count from the Spinbox).
        Outputs: None. Resets the grid, message, and timer.
        """
        # Sourced: Claude AI
        # Cancel a running timer so the old game cannot keep ticking.
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.board = Board(int(self.mine_var.get()))
        self.game_over = False
        self.seconds = 0
        self.status_label.config(text="Playing", fg="#212121")
        self.timer_label.config(text="Time: 0")
        self.refresh()

    def _tick(self) -> None:
        """Advance the on-screen clock by one second and schedule the next tick.

        Inputs:  None.
        Outputs: None. Updates the timer label while the game is running.
        """
        # Sourced: Claude AI
        if self.game_over:
            return
        self.seconds += 1
        self.timer_label.config(text=f"Time: {self.seconds}")
        self.timer_job = self.root.after(1000, self._tick)

    def _start_timer_if_needed(self) -> None:
        """Begin the clock on the player's first reveal.

        Inputs:  None.
        Outputs: None. Does nothing if the timer is already running.
        """
        # Sourced: Claude AI
        if self.timer_job is None and not self.game_over:
            self.timer_job = self.root.after(1000, self._tick)

    def finish(self, won: bool) -> None:
        """End the game: stop the clock, uncover mines, and show the result.

        Inputs:  won (bool) - True if the player cleared the board.
        Outputs: None. Further clicks on the grid are ignored.
        """
        # Sourced: Claude AI
        self.game_over = True
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        if won:
            # A win auto-flags every mine, matching the classic game.
            for row in self.board.grid:
                for cell in row:
                    if cell.is_mine:
                        cell.is_flagged = True
            self.status_label.config(text="Victory", fg="#2e7d32")
        else:
            self.status_label.config(text="Game Over: Loss", fg="#c62828")

        self.refresh(show_mines=not won)

    # ------------------------------------------------------------------
    # Mouse handlers
    # ------------------------------------------------------------------

    def on_left_click(self, row: int, col: int) -> None:
        """Reveal the clicked cell and check for a win or loss.

        Inputs:  row, col (int) - the clicked cell's grid position.
        Outputs: None. Redraws the board.
        """
        # Sourced: Claude AI
        if self.game_over:
            return

        if self.board.reveal(row, col):
            self.finish(won=False)
            return
        # Start the clock only once the board has really been opened. Clicking
        # a flagged cell does nothing, so it must not start the timer either.
        if self.board.mines_placed:
            self._start_timer_if_needed()
        if self.board.is_cleared():
            self.finish(won=True)
            return
        self.refresh()

    def on_right_click(self, row: int, col: int) -> None:
        """Place or remove a flag on the clicked cell.

        Inputs:  row, col (int) - the clicked cell's grid position.
        Outputs: None. Redraws the board.
        """
        # Sourced: Claude AI
        if self.game_over:
            return
        self.board.toggle_flag(row, col)
        self.refresh()

    def on_double_click(self, row: int, col: int) -> None:
        """Open every unflagged neighbor of a number whose flags already match
        its mine count (the classic "chord" shortcut).

        Inputs:  row, col (int) - the double-clicked cell's grid position.
        Outputs: None. Does nothing unless the cell is a revealed number with
                 exactly the right number of flags around it.
        """
        # Sourced: Claude AI
        if self.game_over:
            return
        cell = self.board.grid[row][col]
        if not cell.is_revealed or cell.adjacent_mines == 0:
            return

        # Only safe to chord once the player has flagged as many neighbors as
        # this cell's number claims; otherwise a wrong guess would be punished.
        neighbors = list(self.board.neighbors(row, col))
        flagged = sum(self.board.grid[r][c].is_flagged for r, c in neighbors)
        if flagged != cell.adjacent_mines:
            return

        # Any flag in the wrong place turns this into a losing move, which is
        # exactly how the original game behaves.
        hit_mine = False
        for r, c in neighbors:
            if self.board.reveal(r, c):
                hit_mine = True
        if hit_mine:
            self.finish(won=False)
        elif self.board.is_cleared():
            self.finish(won=True)
        else:
            self.refresh()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def refresh(self, show_mines: bool = False) -> None:
        """Repaint every cell widget to match the current board state.

        Inputs:  show_mines (bool) - if True, draw hidden mines (game over view).
        Outputs: None. Also updates the flags-remaining counter.
        """
        # Sourced: Claude AI
        for r in range(config.ROWS):
            for c in range(config.COLS):
                self._draw_cell(r, c, show_mines)
        # Required display: remaining mine count = total mines minus flags placed.
        self.flags_label.config(text=f"Mines remaining: {self.board.flags_remaining()}")

    def _draw_cell(self, row: int, col: int, show_mines: bool) -> None:
        """Set one cell widget's text, color, and raised/sunken look.

        Inputs:  row, col (int) - cell to draw.
                 show_mines (bool) - reveal hidden mines when True.
        Outputs: None.
        """
        # Sourced: Claude AI
        cell = self.board.grid[row][col]
        widget = self.cells[row][col]

        # --- Still covered: either a flag or a blank raised tile ---
        if not cell.is_revealed:
            if cell.is_flagged:
                widget.config(text="\u2691", fg="#c62828", bg=COVERED_COLOR, relief="raised")
            elif show_mines and cell.is_mine:
                # Game-over view: show the mines the player never found.
                widget.config(text="\u2739", fg="#212121", bg=REVEALED_COLOR, relief="sunken")
            else:
                widget.config(text=" ", bg=COVERED_COLOR, relief="raised")
            return

        # --- Revealed mine: this is the cell that ended the game ---
        if cell.is_mine:
            widget.config(text="\u2739", fg="#212121", bg=MINE_COLOR, relief="sunken")
            return

        # --- Revealed safe cell: blank for 0, otherwise a colored number ---
        count = cell.adjacent_mines
        widget.config(
            text=str(count) if count else " ",
            fg=NUMBER_COLORS.get(count, "#212121"),
            bg=REVEALED_COLOR,
            relief="sunken",
        )


def run() -> None:
    """Open the game window and hand control to Tkinter's event loop.

    Inputs:  None.
    Outputs: None. Returns when the player closes the window.
    """
    # Sourced: Claude AI
    root = tk.Tk()
    MinesweeperGUI(root)
    root.mainloop()
