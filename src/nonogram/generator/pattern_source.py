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
        self._density = density
        self._smoothing_passes = smoothing_passes
        self._rng = random.Random(seed)

    def generate(self, num_rows: int, num_cols: int) -> Grid:
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
        self._grid = grid

    def generate(self, num_rows: int, num_cols: int) -> Grid:
        if self._grid.num_rows != num_rows or self._grid.num_cols != num_cols:
            raise ValueError(
                f"Manual pattern is {self._grid.num_rows}x{self._grid.num_cols}, "
                f"expected {num_rows}x{num_cols}"
            )
        return self._grid


def _smooth(cells, num_rows, num_cols):
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
    cells."""
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
    """Derive (row_clues, col_clues) for a fully-determined pattern grid."""
    row_clues = [line_clue(row) for row in pattern.rows]
    col_clues = [line_clue(col) for col in pattern.columns]
    return row_clues, col_clues
