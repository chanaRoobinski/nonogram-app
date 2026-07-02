from dataclasses import dataclass
from typing import Optional

from nonogram.core.grid import Cell, Grid
from nonogram.solver.engine import SolveStatus, solve


@dataclass
class UniquenessResult:
    is_unique: bool
    first_solution: Optional[Grid]
    alternate_solution: Optional[Grid]


def _forced_cell_grid(n_rows, n_cols, r, c, value):
    rows = [[Cell.UNKNOWN] * n_cols for _ in range(n_rows)]
    rows[r][c] = value
    return Grid(rows)


def _opposite(cell):
    return Cell.EMPTY if cell is Cell.FILLED else Cell.FILLED


def check_uniqueness(row_clues, col_clues, max_backtrack_depth=None) -> UniquenessResult:
    """Determine whether the puzzle described by row_clues/col_clues has exactly
    one valid solution.

    Method: solve the puzzle to find a first solution. Then, for every cell,
    force that cell to the opposite of its value in the first solution (leaving
    every other cell unconstrained) and try to solve again — any second solution
    must differ from the first at some cell, so if none of these per-cell forced
    searches finds an alternative, the first solution is provably unique.

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
                return UniquenessResult(
                    is_unique=False, first_solution=solution, alternate_solution=attempt.grid
                )

    return UniquenessResult(is_unique=True, first_solution=solution, alternate_solution=None)


def has_unique_solution(row_clues, col_clues, max_backtrack_depth=None) -> bool:
    return check_uniqueness(row_clues, col_clues, max_backtrack_depth).is_unique
