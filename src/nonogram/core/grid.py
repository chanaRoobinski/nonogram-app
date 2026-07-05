"""Core data structures shared across the whole project: the puzzle "clue"
vocabulary (Clue), individual cell state (Cell), a row/column of cells
(Line), and the full puzzle grid (Grid). Nothing in this module depends on
any other part of the codebase — every other package (solver, difficulty,
generator, api) builds on top of these three types.
"""

from enum import Enum, auto

from nonogram.core.exceptions import InvalidClueError


class Clue:
    """An ordered sequence of run lengths for one row or column.

    A nonogram clue like "3 1" means: somewhere in this line there is a run
    of 3 filled cells, then (after at least one empty cell) a run of 1 filled
    cell, in that order, with no other filled cells. ``Clue([3, 1])``
    represents exactly that.

    A fully empty line is represented as ``Clue([])``, not ``Clue([0])`` —
    every value in a non-empty clue is a positive run length (>= 1). This
    keeps the invariant simple: every element of ``runs`` is a real,
    non-zero run, so no code downstream has to special-case a "0" entry.

    Clue is immutable and hashable so it can be freely compared, put in
    sets, and used as a dict key.
    """

    def __init__(self, runs):
        """Validate and store the run lengths.

        Raises InvalidClueError if any value is not a plain positive
        integer (bools are rejected too, since ``True``/``False`` are
        technically ``int`` subclasses in Python but are never a
        meaningful run length).
        """
        runs = tuple(runs)
        for run in runs:
            if isinstance(run, bool) or not isinstance(run, int):
                raise InvalidClueError(f"Clue values must be integers, got {run!r}")
            if run < 1:
                raise InvalidClueError(f"Clue values must be >= 1, got {run}")
        self.runs = runs

    def __len__(self):
        """Number of runs in this clue (0 for a fully empty line)."""
        return len(self.runs)

    def __iter__(self):
        """Iterate over the run lengths in order, e.g. list(Clue([3, 1])) == [3, 1]."""
        return iter(self.runs)

    def __getitem__(self, index):
        """Access a single run length by position, e.g. Clue([3, 1])[0] == 3."""
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
    """The three possible states of a single grid cell while solving.

    UNKNOWN means "not yet determined" — this is the state every cell
    starts in before any solving happens. FILLED and EMPTY are the two
    final states a cell can settle into. Using an Enum (rather than e.g.
    True/False/None) makes the "not yet known" state a first-class,
    unambiguous value instead of an overloaded sentinel.
    """

    UNKNOWN = auto()
    FILLED = auto()
    EMPTY = auto()


class Line:
    """An immutable row or column: a fixed-length sequence of Cell values.

    Line doesn't know whether it's a row or a column, or which Clue it's
    supposed to satisfy — it's just "some cells in a row", used both for
    grid rows/columns and as the input/output of the single-line solver
    (solver/line_solver.py).
    """

    def __init__(self, cells):
        """Store the cells, raising TypeError if any element isn't a Cell."""
        cells = tuple(cells)
        for cell in cells:
            if not isinstance(cell, Cell):
                raise TypeError(f"Line cells must be Cell values, got {cell!r}")
        self.cells = cells

    @classmethod
    def unknown(cls, length):
        """Build a Line of the given length with every cell UNKNOWN — the
        starting state for a line that hasn't been solved at all yet."""
        return cls([Cell.UNKNOWN] * length)

    def __len__(self):
        return len(self.cells)

    def __iter__(self):
        """Iterate over the cells in order."""
        return iter(self.cells)

    def __getitem__(self, index):
        """Access a single cell by position, e.g. line[0]."""
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
    """A rectangular matrix of cells, accessible both by row and by column.

    Grid deliberately stores only cell state — it does NOT hold the row/
    column Clues for the puzzle it represents. Clues are tracked separately
    (as parallel lists of row_clues/col_clues) by whatever code is using
    the Grid, and matched to rows/columns by index. This keeps Grid a pure
    "what's filled in right now" snapshot, reusable both as a fully-solved
    solution and as a partially-solved in-progress state.
    """

    def __init__(self, rows):
        """Build a Grid from an iterable of rows, where each row is either
        already a Line or any iterable of Cell values. Raises ValueError if
        the rows don't all have the same length (a Grid must be a proper
        rectangle)."""
        rows = tuple(row if isinstance(row, Line) else Line(row) for row in rows)
        if rows:
            width = len(rows[0])
            for row in rows:
                if len(row) != width:
                    raise ValueError("All rows in a Grid must have the same length")
        self._rows = rows

    @classmethod
    def empty(cls, num_rows, num_cols):
        """Build a num_rows x num_cols Grid with every cell UNKNOWN — the
        starting point for solving a puzzle from scratch."""
        return cls([Line.unknown(num_cols) for _ in range(num_rows)])

    @property
    def num_rows(self):
        return len(self._rows)

    @property
    def num_cols(self):
        """0 for a Grid with no rows at all, since there's no row to measure."""
        return len(self._rows[0]) if self._rows else 0

    @property
    def rows(self):
        """All rows, top to bottom, as a tuple of Line."""
        return self._rows

    @property
    def columns(self):
        """All columns, left to right, as a tuple of Line — computed on
        access by reading down each column index (see column())."""
        return tuple(self.column(i) for i in range(self.num_cols))

    def row(self, index):
        """The row at the given 0-based index."""
        return self._rows[index]

    def column(self, index):
        """The column at the given 0-based index, built by reading the cell
        at that index from every row, top to bottom."""
        return Line(row[index] for row in self._rows)

    def transpose(self):
        """A new Grid with rows and columns swapped: transpose().row(i) ==
        column(i) for every valid i. Used by the solver to run the same
        single-line logic on columns as on rows."""
        return Grid(self.columns)

    def __eq__(self, other):
        if not isinstance(other, Grid):
            return NotImplemented
        return self._rows == other._rows

    def __repr__(self):
        return f"Grid({[list(row) for row in self._rows]!r})"
