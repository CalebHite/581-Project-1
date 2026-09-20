# Minesweeper — EECS 581 Project 1

A single-player Minesweeper game on a 10x10 grid (columns **A–J**, rows **1–10**) with a
user-selected mine count of 10–20. Ships with a clickable graphical window (Tkinter) and a
terminal version.

**Course:** EECS 581 Software Engineering II, Fall 2026 — Professor Hossein Saiedian

---

## Running the game

Requires Python 3.9+ (developed and tested on 3.11). No third-party packages.

```bash
python main.py            # graphical window (default)
python main.py --text     # terminal version
```

If Tkinter is missing from your Python installation, `main.py` explains how to install it
and falls back to the terminal version rather than crashing.

### Running the tests

```bash
python -m unittest discover -s tests -t .
```

---

## How to play

### Graphical version

| Action | Effect |
| --- | --- |
| Left-click | Uncover a cell |
| Right-click (or Ctrl-click on macOS) | Place / remove a flag |
| Double-click a number | "Chord" — open all unflagged neighbors once the flag count matches the number |
| **Mines** spinner | Choose 10–20 mines (enforced by the control, so an invalid count can never be entered) |
| **New Game** | Start a fresh board |

The window shows **Mines remaining** (total mines minus flags placed), an elapsed timer, and
a status indicator reading **Playing**, **Victory**, or **Game Over: Loss**.

### Terminal version

```
Commands: 'r A1' to reveal, 'f A1' to flag/unflag, 'q' to quit.
```

Coordinates are case-insensitive (`A1`, `a1`, and ` A1 ` are all accepted). Invalid
coordinates and malformed commands print an explanation and re-prompt instead of exiting.

Board symbols: `#` covered · `F` flagged · `.` uncovered with zero adjacent mines ·
`1`–`8` adjacent mine count · `*` mine (shown at game over).

---

## Requirement coverage

| Requirement | Where it is implemented |
| --- | --- |
| 10x10 grid, columns A–J, rows 1–10 | `minesweeper/config.py` (`ROWS`, `COLS`, `COL_LABELS`) |
| Mine count user-specified, 10–20 | GUI spinner (`gui.py::_build_control_bar`); terminal prompt (`game.py::prompt_mine_count`); enforced in `Board.__init__` |
| Mines randomly placed at game start | `Board.place_mines` via `random.Random.sample` |
| First clicked cell (and neighbors) guaranteed mine-free | `Board.place_mines` builds a safe set; mines are placed lazily on the first real reveal. Neighbor safety toggled by `config.SAFE_NEIGHBORS_ON_FIRST_CLICK` |
| All cells start covered, no flags | `Cell` dataclass defaults |
| Uncovering a mine ends the game (loss) | `Board.reveal` returns `True`; handled by `gui.py::finish` / `game.py::play` |
| Number 0–8 of adjacent mines | `Cell.adjacent_mines`, computed in `Board.place_mines` |
| Zero-adjacent cells recursively uncover neighbors | Iterative flood fill in `Board.reveal` |
| Toggle flags on covered cells | `Board.toggle_flag` |
| Flagged cells cannot be uncovered until unflagged | Guard at the top of `Board.reveal` |
| Display remaining flag/mine count | `Board.flags_remaining`, shown in both front ends |
| Grid display of covered / flagged / uncovered states | `gui.py::_draw_cell`; `Cell.symbol` + `Board.render` |
| Status indicator | Status label in the GUI; `Status:` line in the terminal version |
| Loss reveals all mines | `refresh(show_mines=True)` / `render(show_mines=True)` |
| Win by uncovering all non-mine cells | `Board.is_cleared` |

---

## Repository contents

```
main.py                     Entry point; picks the GUI or terminal front end
minesweeper/
  __init__.py               Package marker
  config.py                 Board size, column labels, mine limits, first-click rule
  cell.py                   Cell dataclass (one square's state + display symbol)
  board.py                  Board Manager + Game Logic: grid, mines, reveal, flags, win check
  game.py                   Terminal front end (UI + input handler)
  gui.py                    Tkinter front end (UI + input handler)
tests/
  test_board.py             Coordinate parsing, board setup, first-click safety
  test_game_logic.py        Gameplay, flagging, win/loss, bounds, randomized stress test
EECS 581 P1 Team Meeting Log.docx
EECS 581 Project 1 Estimated Person Hours.pages
```

---

## Source attribution

Portions of this project were generated with the assistance of **Claude (Anthropic, model
Claude Opus 5)** via Claude Code, prompted with the project requirements, and reviewed by the
authors. Every source file carries a prologue comment naming its author, creation date, and
external sources; in-code comments marked `# Sourced: Claude AI` indicate AI-assisted blocks.

Standard-library documentation referenced: [`random`](https://docs.python.org/3/library/random.html),
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
[`tkinter`](https://docs.python.org/3/library/tkinter.html),
[`unittest`](https://docs.python.org/3/library/unittest.html).
The flood-fill reveal uses the standard iterative depth-first search technique (common
algorithm; no specific source copied). The cell number colors follow the classic Minesweeper
palette.

## Team

| Member | Role / Task |
| --- | --- |
| Bradley Brown | Scrum Master |
| Caleb Hite | Software Engineer — Game setup |
| Ben Haney | Software Engineer — Game conclusion |
| Will Calhoun | Software Engineer — Player interface |
| Charlie Doherty | Software Engineer — Gameplay function |
| Kai Barnhart | Software Engineer — Flag setting |
