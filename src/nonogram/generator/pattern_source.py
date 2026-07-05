"""Sources of candidate solution patterns for the puzzle generator, plus the
utilities to turn a finished pattern into the row/column clues that describe
it as a nonogram puzzle.

A "pattern" here just means a fully-filled-in Grid (no UNKNOWN cells) that
will become a puzzle's *solution* — puzzle_generator.py takes a pattern,
derives its clues via extract_clues(), and checks whether those clues make a
good puzzle (unique solution, reasonable difficulty) before offering it.
"""

import random
from abc import ABC, abstractmethod

from nonogram.core.grid import Cell, Clue, Grid


class PatternSource(ABC):
    """A source of candidate solution patterns for the puzzle generator. Random
    generation is implemented now; an image-based source is planned for a
    future phase (see image_recognition/interface.py) and can be added later
    as another implementation of this same interface."""

    @abstractmethod
    def generate(self, num_rows: int, num_cols: int) -> Grid:
        """Return a fully-determined (no UNKNOWN cells) candidate pattern of
        the requested size."""


class RandomPatternSource(PatternSource):
    """Generates patterns via random noise followed by a majority-rule
    smoothing pass, which consolidates "salt and pepper" noise into more
    contiguous, picture-like regions."""

    def __init__(self, density=0.45, smoothing_passes=2, seed=None):
        """density: the probability any given cell starts out FILLED, before
        smoothing (0.45 tends to produce patterns that are neither almost
        empty nor almost solid). smoothing_passes: how many times to apply
        the neighbor-majority smoothing step. seed: passed straight to
        random.Random — set it for reproducible/deterministic output
        (e.g. in tests), or leave it None for genuinely random patterns."""
        self._density = density
        self._smoothing_passes = smoothing_passes
        self._rng = random.Random(seed)

    def generate(self, num_rows: int, num_cols: int) -> Grid:
        """Build a random pattern: first fill every cell independently at
        random (biased by `density`), then run the smoothing pass
        `smoothing_passes` times to consolidate the noise into blockier,
        more picture-like shapes."""
        cells = [
            [
                Cell.FILLED if self._rng.random() < self._density else Cell.EMPTY
                for _ in range(num_cols)
            ]
            for _ in range(num_rows)
        ]
        for _ in range(self._smoothing_passes):
            cells = _smooth(cells, num_rows, num_cols)
        return Grid(cells)


class ManualPatternSource(PatternSource):
    """Wraps a hand-specified pattern so it can be fed through the same
    generate-and-test pipeline as random patterns."""

    def __init__(self, grid: Grid):
        """grid: the fixed pattern this source will always return."""
        self._grid = grid

    def generate(self, num_rows: int, num_cols: int) -> Grid:
        """Return the wrapped grid, as long as its dimensions match what
        was requested. Raises ValueError on a size mismatch — this source
        can't "generate" a different size, it can only replay the one
        pattern it was given."""
        if self._grid.num_rows != num_rows or self._grid.num_cols != num_cols:
            raise ValueError(
                f"Manual pattern is {self._grid.num_rows}x{self._grid.num_cols}, "
                f"expected {num_rows}x{num_cols}"
            )
        return self._grid


def _smooth(cells, num_rows, num_cols):
    """One pass of a majority-rule cellular-automaton smoothing step: each
    cell becomes FILLED if at least half of its up-to-8 neighbors (fewer at
    the grid's edges/corners) are FILLED, else EMPTY. Applied repeatedly,
    this tends to erode isolated single cells and grow larger contiguous
    blobs, which is what turns uniform random noise into more picture-like
    shapes."""
    smoothed = [[Cell.EMPTY] * num_cols for _ in range(num_rows)]
    for r in range(num_rows):
        for c in range(num_cols):
            filled_neighbors = 0
            total_neighbors = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < num_rows and 0 <= nc < num_cols:
                        total_neighbors += 1
                        if cells[nr][nc] is Cell.FILLED:
                            filled_neighbors += 1
            smoothed[r][c] = (
                Cell.FILLED if filled_neighbors >= total_neighbors / 2 else Cell.EMPTY
            )
    return smoothed


def line_clue(cells) -> Clue:
    """Derive the Clue (run lengths) for a single row/column of FILLED/EMPTY
    cells: scan left to right, counting consecutive FILLED cells as one run,
    ended by any EMPTY cell (or the end of the line)."""
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


def extract_clues(pattern: Grid):
    """Derive (row_clues, col_clues) for a fully-determined pattern grid —
    i.e. work out what puzzle clues would describe this exact solution, by
    applying line_clue() to every row and every column."""
    row_clues = [line_clue(row) for row in pattern.rows]
    col_clues = [line_clue(col) for col in pattern.columns]
    return row_clues, col_clues
