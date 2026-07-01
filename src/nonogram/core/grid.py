from enum import Enum, auto

from nonogram.core.exceptions import InvalidClueError


class Clue:
    """An ordered sequence of run lengths for one row or column.

    A fully empty line is represented as ``Clue([])``, not ``Clue([0])`` — every
    value in a non-empty clue is a positive run length (>= 1).
    """

    def __init__(self, runs):
        runs = tuple(runs)
        for run in runs:
            if isinstance(run, bool) or not isinstance(run, int):
                raise InvalidClueError(f"Clue values must be integers, got {run!r}")
            if run < 1:
                raise InvalidClueError(f"Clue values must be >= 1, got {run}")
        self.runs = runs

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        return iter(self.runs)

    def __getitem__(self, index):
        return self.runs[index]

    def __eq__(self, other):
        if not isinstance(other, Clue):
            return NotImplemented
        return self.runs == other.runs

    def __hash__(self):
        return hash(self.runs)

    def __repr__(self):
        return f"Clue({list(self.runs)!r})"


class Cell(Enum):
    UNKNOWN = auto()
    FILLED = auto()
    EMPTY = auto()


class Line:
    """An immutable row/column of cells."""

    def __init__(self, cells):
        cells = tuple(cells)
        for cell in cells:
            if not isinstance(cell, Cell):
                raise TypeError(f"Line cells must be Cell values, got {cell!r}")
        self.cells = cells

    @classmethod
    def unknown(cls, length):
        return cls([Cell.UNKNOWN] * length)

    def __len__(self):
        return len(self.cells)

    def __iter__(self):
        return iter(self.cells)

    def __getitem__(self, index):
        return self.cells[index]

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return self.cells == other.cells

    def __hash__(self):
        return hash(self.cells)

    def __repr__(self):
        return f"Line({list(self.cells)!r})"


class Grid:
    """A matrix of cells, accessible both by row and by column."""

    def __init__(self, rows):
        rows = tuple(row if isinstance(row, Line) else Line(row) for row in rows)
        if rows:
            width = len(rows[0])
            for row in rows:
                if len(row) != width:
                    raise ValueError("All rows in a Grid must have the same length")
        self._rows = rows

    @classmethod
    def empty(cls, num_rows, num_cols):
        return cls([Line.unknown(num_cols) for _ in range(num_rows)])

    @property
    def num_rows(self):
        return len(self._rows)

    @property
    def num_cols(self):
        return len(self._rows[0]) if self._rows else 0

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return tuple(self.column(i) for i in range(self.num_cols))

    def row(self, index):
        return self._rows[index]

    def column(self, index):
        return Line(row[index] for row in self._rows)

    def transpose(self):
        return Grid(self.columns)

    def __eq__(self, other):
        if not isinstance(other, Grid):
            return NotImplemented
        return self._rows == other._rows

    def __repr__(self):
        return f"Grid({[list(row) for row in self._rows]!r})"
