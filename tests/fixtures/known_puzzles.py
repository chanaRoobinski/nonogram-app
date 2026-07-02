"""Known puzzles (grid + row/column clues + solution) used as fixtures across
solver test suites. Clues are derived automatically from each hand-authored
solution so they can never drift out of sync with it."""

from dataclasses import dataclass

from nonogram.core.grid import Cell, Clue, Grid


@dataclass(frozen=True)
class KnownPuzzle:
    name: str
    row_clues: list
    col_clues: list
    solution: Grid


def _line_clue(cells):
    runs = []
    run_length = 0
    for cell in cells:
        if cell is Cell.FILLED:
            run_length += 1
        else:
            if run_length:
                runs.append(run_length)
            run_length = 0
    if run_length:
        runs.append(run_length)
    return Clue(runs)


def _solution_from_strings(rows):
    return Grid(
        [[Cell.FILLED if ch == "#" else Cell.EMPTY for ch in row] for row in rows]
    )


def _puzzle_from_solution(name, rows_as_strings):
    solution = _solution_from_strings(rows_as_strings)
    row_clues = [_line_clue(row) for row in solution.rows]
    col_clues = [_line_clue(col) for col in solution.columns]
    return KnownPuzzle(name, row_clues, col_clues, solution)


# Solvable by row/column propagation alone (no guessing required).
PLUS_SIGN_5X5 = _puzzle_from_solution(
    "plus_sign_5x5",
    [
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
    ],
)

# Solvable by row/column propagation alone (no guessing required).
FRAME_10X10 = _puzzle_from_solution(
    "frame_10x10",
    [
        "##########",
        "#........#",
        "#.######.#",
        "#.#....#.#",
        "#.#.##.#.#",
        "#.#.##.#.#",
        "#.#....#.#",
        "#.######.#",
        "#........#",
        "##########",
    ],
)

# Deliberately ambiguous under pure line-by-line propagation (every row/column
# clue is a single run of 1 in a width/height of 2, so no cell is ever forced) —
# requires backtracking to resolve.
CHECKERBOARD_4X4 = _puzzle_from_solution(
    "checkerboard_4x4",
    [
        "#.#.",
        ".#.#",
        "#.#.",
        ".#.#",
    ],
)

ALL_KNOWN_PUZZLES = [PLUS_SIGN_5X5, FRAME_10X10, CHECKERBOARD_4X4]
