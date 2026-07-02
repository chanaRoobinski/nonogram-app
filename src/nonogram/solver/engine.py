from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from nonogram.core.exceptions import ContradictionError
from nonogram.core.grid import Cell, Grid, Line
from nonogram.solver.line_solver import solve_line


@dataclass
class PropagationStats:
    lines_solved: int = 0
    cells_deduced: int = 0


@dataclass
class SolveStats:
    """Statistics accumulated over a full solve() run, intended to feed the
    difficulty evaluator (Stage 5): how much of the puzzle was resolved by pure
    constraint propagation versus how much required guess-and-backtrack search."""

    propagation_calls: int = 0
    lines_solved: int = 0
    cells_deduced_by_propagation: int = 0
    guesses: int = 0
    max_backtrack_depth: int = 0


class SolveStatus(Enum):
    SOLVED = auto()
    CONTRADICTION = auto()
    MAX_DEPTH_EXCEEDED = auto()


@dataclass
class SolveResult:
    status: SolveStatus
    grid: Optional[Grid]
    stats: SolveStats = field(default_factory=SolveStats)


class _MaxDepthExceeded(Exception):
    pass


def propagate(grid, row_clues, col_clues, dirty_rows=None, dirty_cols=None):
    """Run solve_line on rows/columns alternately until no further change occurs,
    only re-checking lines that were "woken up" by a change in the perpendicular
    direction. Returns (new_grid, PropagationStats).

    dirty_rows/dirty_cols let a caller limit the initial work list to lines known
    to have changed (e.g. after a single-cell backtracking guess), instead of
    re-checking the whole grid. Defaults to checking every row and column.
    """
    n_rows, n_cols = grid.num_rows, grid.num_cols
    cells = [list(row) for row in grid.rows]
    stats = PropagationStats()

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
                    dirty_rows.add(r)

    return Grid([Line(row) for row in cells]), stats


def _is_fully_solved(grid):
    return all(cell is not Cell.UNKNOWN for row in grid.rows for cell in row)


def _first_unknown_cell(grid):
    """Only called when the grid is known not to be fully solved, so this
    always finds a match."""
    for r, row in enumerate(grid.rows):
        for c, cell in enumerate(row):
            if cell is Cell.UNKNOWN:
                return r, c


def _with_cell(grid, r, c, value):
    rows = [list(row) for row in grid.rows]
    rows[r][c] = value
    return Grid([Line(row) for row in rows])


def _solve_recursive(
    grid, row_clues, col_clues, stats, depth, max_backtrack_depth, dirty_rows, dirty_cols
):
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
            return _solve_recursive(
                guessed, row_clues, col_clues, stats, depth + 1, max_backtrack_depth, {r}, {c}
            )
        except ContradictionError:
            continue

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
