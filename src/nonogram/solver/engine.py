"""The full-grid solver: assembles the single-line solver (line_solver.py)
into something that can solve a whole puzzle.

Two layers:
  - propagate(): repeatedly re-runs solve_line on rows and columns,
    bouncing information back and forth between them, until nothing more
    can be deduced by pure logic alone.
  - solve(): calls propagate(), and if the grid still isn't fully solved
    (propagation alone wasn't enough — some puzzles genuinely require
    "what if?" reasoning), picks an unknown cell, guesses a value, and
    recurses, backtracking if a guess turns out to be wrong. This is a
    standard backtracking search: try something, and if it leads to a
    contradiction, undo it and try the alternative.

Along the way, solve() also collects SolveStats — how much was solved by
plain propagation vs. how many guesses/how much nested backtracking was
needed — which Stage 5's difficulty evaluator turns into a difficulty score.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from nonogram.core.exceptions import ContradictionError
from nonogram.core.grid import Cell, Grid, Line
from nonogram.solver.line_solver import solve_line


@dataclass
class PropagationStats:
    """Counters for a single propagate() call."""

    lines_solved: int = 0
    """How many times solve_line() was called (one call per row/column re-check)."""

    cells_deduced: int = 0
    """How many individual cells changed from UNKNOWN to a known value."""


@dataclass
class SolveStats:
    """Statistics accumulated over a full solve() run, intended to feed the
    difficulty evaluator (Stage 5): how much of the puzzle was resolved by pure
    constraint propagation versus how much required guess-and-backtrack search."""

    propagation_calls: int = 0
    """How many times propagate() was invoked in total — once for the
    initial pass, plus once for every guess tried during backtracking."""

    lines_solved: int = 0
    """Total solve_line() calls across every propagate() invocation."""

    cells_deduced_by_propagation: int = 0
    """Total cells resolved by pure logical deduction (never guessed)."""

    guesses: int = 0
    """Total number of "what if this cell were FILLED/EMPTY?" branches
    tried during backtracking (including ones that failed and were
    undone)."""

    max_backtrack_depth: int = 0
    """The deepest level of *nested* guessing reached anywhere in the
    search. 0 means the puzzle was solved by propagation alone, with no
    guessing needed at all."""


class SolveStatus(Enum):
    """The three possible outcomes of a solve() call."""

    SOLVED = auto()
    """A complete, valid solution was found."""

    CONTRADICTION = auto()
    """The given clues admit no valid solution at all — every guess,
    at every level, eventually hit a dead end."""

    MAX_DEPTH_EXCEEDED = auto()
    """A caller-supplied max_backtrack_depth was hit before a solution (or
    a definitive contradiction) could be found. The puzzle might still be
    solvable with a higher depth limit — this status just means the search
    gave up early."""


@dataclass
class SolveResult:
    """The outcome of a solve() call: what happened (status), the solved
    Grid if status is SOLVED (None otherwise), and the SolveStats collected
    along the way (useful for difficulty scoring even when solving failed)."""

    status: SolveStatus
    grid: Optional[Grid]
    stats: SolveStats = field(default_factory=SolveStats)


class _MaxDepthExceeded(Exception):
    """Internal signal used to unwind out of _solve_recursive once
    max_backtrack_depth is hit. Never exposed outside this module — solve()
    catches it and reports SolveStatus.MAX_DEPTH_EXCEEDED instead."""


def propagate(grid, row_clues, col_clues, dirty_rows=None, dirty_cols=None):
    """Run solve_line on rows/columns alternately until no further change occurs,
    only re-checking lines that were "woken up" by a change in the perpendicular
    direction. Returns (new_grid, PropagationStats).

    dirty_rows/dirty_cols let a caller limit the initial work list to lines known
    to have changed (e.g. after a single-cell backtracking guess), instead of
    re-checking the whole grid. Defaults to checking every row and column.
    """
    n_rows, n_cols = grid.num_rows, grid.num_cols
    # Cells are tracked as a plain mutable 2D list here (rather than
    # rebuilding immutable Line/Grid objects on every single change) purely
    # for performance — propagate() can touch a lot of cells before it's done.
    cells = [list(row) for row in grid.rows]
    stats = PropagationStats()

    # dirty_rows/dirty_cols form a work queue: "these lines might have new
    # information to extract, go check them." Every row/column starts dirty
    # unless the caller says otherwise (e.g. after a single guessed cell,
    # only that one row and column need an initial check).
    dirty_rows = set(range(n_rows)) if dirty_rows is None else set(dirty_rows)
    dirty_cols = set(range(n_cols)) if dirty_cols is None else set(dirty_cols)

    while dirty_rows or dirty_cols:
        if dirty_rows:
            r = dirty_rows.pop()
            new_line = solve_line(row_clues[r], Line(cells[r]))
            stats.lines_solved += 1
            for c in range(n_cols):
                if cells[r][c] != new_line[c]:
                    cells[r][c] = new_line[c]
                    stats.cells_deduced += 1
                    # This row just gave us new information about column c —
                    # column c needs to be re-checked in light of it.
                    dirty_cols.add(c)
        else:
            c = dirty_cols.pop()
            column = Line(cells[r][c] for r in range(n_rows))
            new_line = solve_line(col_clues[c], column)
            stats.lines_solved += 1
            for r in range(n_rows):
                if cells[r][c] != new_line[r]:
                    cells[r][c] = new_line[r]
                    stats.cells_deduced += 1
                    # Symmetric to the row case: wake up the affected row.
                    dirty_rows.add(r)

    return Grid([Line(row) for row in cells]), stats


def _is_fully_solved(grid):
    """True once every cell has moved past UNKNOWN — meaning a complete
    (and, by construction, internally consistent) solution has been found."""
    return all(cell is not Cell.UNKNOWN for row in grid.rows for cell in row)


def _first_unknown_cell(grid):
    """The first still-UNKNOWN cell, scanning row by row, left to right —
    used to pick which cell to guess next during backtracking. Only called
    when the grid is known not to be fully solved, so this always finds a
    match."""
    for r, row in enumerate(grid.rows):
        for c, cell in enumerate(row):
            if cell is Cell.UNKNOWN:
                return r, c


def _with_cell(grid, r, c, value):
    """A copy of `grid` with cell (r, c) forced to `value`, used to try out
    a guess without mutating the original grid (so it's still available if
    the guess needs to be undone)."""
    rows = [list(row) for row in grid.rows]
    rows[r][c] = value
    return Grid([Line(row) for row in rows])


def _solve_recursive(
    grid, row_clues, col_clues, stats, depth, max_backtrack_depth, dirty_rows, dirty_cols
):
    """One node of the backtracking search: propagate as far as possible
    from the current grid state, and if that alone doesn't finish the
    puzzle, guess a cell's value and recurse — trying FILLED first, then
    EMPTY, undoing (via the ContradictionError catch) and trying the other
    option if the first guess leads to a dead end."""
    propagated, prop_stats = propagate(grid, row_clues, col_clues, dirty_rows, dirty_cols)
    stats.propagation_calls += 1
    stats.lines_solved += prop_stats.lines_solved
    stats.cells_deduced_by_propagation += prop_stats.cells_deduced

    if _is_fully_solved(propagated):
        return propagated

    if max_backtrack_depth is not None and depth >= max_backtrack_depth:
        raise _MaxDepthExceeded()

    stats.max_backtrack_depth = max(stats.max_backtrack_depth, depth + 1)

    r, c = _first_unknown_cell(propagated)
    for guess in (Cell.FILLED, Cell.EMPTY):
        stats.guesses += 1
        guessed = _with_cell(propagated, r, c, guess)
        try:
            # Only (r, c)'s row and column are marked dirty here (not the
            # whole grid) since everything else is already as fully
            # propagated as it can be — only this one new guess needs
            # re-checking, which keeps backtracking fast.
            return _solve_recursive(
                guessed, row_clues, col_clues, stats, depth + 1, max_backtrack_depth, {r}, {c}
            )
        except ContradictionError:
            # This guess was wrong — fall through and try the other value.
            continue

    # Neither FILLED nor EMPTY worked at this cell: this whole branch (the
    # grid state we were given) has no valid solution. Let the caller (the
    # guess one level up, if any) know so *it* can try its other option.
    raise ContradictionError("No valid arrangement found after exhausting guesses")


def solve(grid, row_clues, col_clues, max_backtrack_depth=None):
    """Solve a nonogram grid: propagate constraints, falling back to guess-and-
    backtrack when propagation alone cannot resolve a cell. `max_backtrack_depth`
    caps how many nested guesses may be made (None = unlimited)."""
    stats = SolveStats()
    try:
        solved_grid = _solve_recursive(
            grid, row_clues, col_clues, stats, 0, max_backtrack_depth, None, None
        )
    except ContradictionError:
        return SolveResult(SolveStatus.CONTRADICTION, None, stats)
    except _MaxDepthExceeded:
        return SolveResult(SolveStatus.MAX_DEPTH_EXCEEDED, None, stats)
    return SolveResult(SolveStatus.SOLVED, solved_grid, stats)
