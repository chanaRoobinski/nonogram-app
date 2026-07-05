"""Checks whether a puzzle (a set of row/column clues) has exactly one valid
solution — important because a "real" nonogram puzzle should always have a
single, unambiguous answer. The generator (generator/puzzle_generator.py)
uses this to reject any randomly-produced pattern that turns out to admit
more than one solution before offering it to a player.
"""

from dataclasses import dataclass
from typing import Optional

from nonogram.core.grid import Cell, Grid
from nonogram.solver.engine import SolveStatus, solve


@dataclass
class UniquenessResult:
    """The outcome of check_uniqueness(): whether the puzzle has exactly one
    solution, plus the solutions found along the way (useful for debugging
    or for showing *why* a puzzle was rejected as ambiguous)."""

    is_unique: bool
    """True only if exactly one valid solution exists."""

    first_solution: Optional[Grid]
    """The first solution found, or None if the puzzle has no solution at all."""

    alternate_solution: Optional[Grid]
    """A second, genuinely different solution, if one was found (proving
    the puzzle is *not* unique). None if the puzzle is unique or unsolvable."""


def _forced_cell_grid(n_rows, n_cols, r, c, value):
    """A blank (all-UNKNOWN) grid of the given size, except cell (r, c) is
    forced to `value`. Used to ask "is there *any* valid solution where this
    one cell differs from what we already found?", with every other cell
    left free for the solver to work out from scratch."""
    rows = [[Cell.UNKNOWN] * n_cols for _ in range(n_rows)]
    rows[r][c] = value
    return Grid(rows)


def _opposite(cell):
    """The other of FILLED/EMPTY — used to ask "what if this cell were the
    other way around?" when probing for a second solution."""
    return Cell.EMPTY if cell is Cell.FILLED else Cell.FILLED


def check_uniqueness(row_clues, col_clues, max_backtrack_depth=None) -> UniquenessResult:
    """Determine whether the puzzle described by row_clues/col_clues has exactly
    one valid solution.

    Method: solve the puzzle to find a first solution. Then, for every cell,
    force that cell to the opposite of its value in the first solution (leaving
    every other cell unconstrained) and try to solve again — any second solution
    must differ from the first at some cell, so if none of these per-cell forced
    searches finds an alternative, the first solution is provably unique.

    Why check *every* cell, not just one: forcing a single arbitrary cell only
    proves that one specific cell has no alternative — it says nothing about
    whether some *other* cell could differ in a second solution. Only after
    every cell has been tried and none produced an alternative can we be sure
    no second solution exists anywhere.

    A puzzle with no solution at all is not "unique" (there is nothing to be
    unique) and is reported as is_unique=False.
    """
    n_rows, n_cols = len(row_clues), len(col_clues)
    first = solve(Grid.empty(n_rows, n_cols), row_clues, col_clues, max_backtrack_depth)
    if first.status is not SolveStatus.SOLVED:
        return UniquenessResult(is_unique=False, first_solution=None, alternate_solution=None)

    solution = first.grid
    for r in range(n_rows):
        for c in range(n_cols):
            forced_value = _opposite(solution.row(r)[c])
            forced_grid = _forced_cell_grid(n_rows, n_cols, r, c, forced_value)
            attempt = solve(forced_grid, row_clues, col_clues, max_backtrack_depth)
            if attempt.status is SolveStatus.SOLVED:
                # Found a genuinely different valid solution — not unique.
                # No need to check the remaining cells.
                return UniquenessResult(
                    is_unique=False, first_solution=solution, alternate_solution=attempt.grid
                )

    # Every cell was tried and none admitted an alternative solution: the
    # first solution found is the only one that exists.
    return UniquenessResult(is_unique=True, first_solution=solution, alternate_solution=None)


def has_unique_solution(row_clues, col_clues, max_backtrack_depth=None) -> bool:
    """Convenience wrapper around check_uniqueness() for callers that only
    need the yes/no answer, not the solutions themselves."""
    return check_uniqueness(row_clues, col_clues, max_backtrack_depth).is_unique
