"""Single-line constraint solving: given one row/column's Clue and whatever
is already known about that line, figure out which additional cells are
*logically forced* to be FILLED or EMPTY, purely by reasoning about that one
line in isolation (no information from other rows/columns is used here —
that cross-referencing happens one level up, in solver/engine.py).

The algorithm (in solve_line, below) is a dynamic-programming feasibility
check, run twice — once left-to-right ("forward") and once right-to-left
("backward") — and then combined. The core idea: a clue like [3, 1] can be
thought of as a tiny pattern the line must match — some EMPTY cells, then a
run of 3 FILLED cells, then at least 1 EMPTY cell (the mandatory gap), then a
run of 1 FILLED cell, then more EMPTY cells. "forward" and "backward" each
answer "is it *possible* to reach this point in the line, having placed
exactly this many runs so far, consistent with what's already known?" for
every position and every count of runs placed. Combining both directions
lets us ask, for every single cell: "is there at least one full arrangement
where this cell is FILLED?" and the same question for EMPTY. If only one
answer is ever "yes", that cell's value is certain.
"""

from nonogram.core.exceptions import ContradictionError
from nonogram.core.grid import Cell, Clue, Line


def _compatible(cell: Cell, value: Cell) -> bool:
    """Can this already-known cell hold `value`? UNKNOWN cells can hold
    anything; a cell already known to be FILLED or EMPTY can only "hold"
    that same value."""
    return cell is Cell.UNKNOWN or cell is value


def _prefix_gap(run_index: int) -> int:
    """How many mandatory EMPTY cells must immediately precede this run.

    Every run needs at least one EMPTY cell separating it from the run
    before it — except the very first run (index 0), which can start right
    at the beginning of the line with no gap required."""
    return 1 if run_index > 0 else 0


def _can_place_run(current_state: Line, start: int, run_index: int, runs: list) -> tuple:
    """Check whether `runs[run_index]` — together with its mandatory
    leading gap, if any — can be placed starting at position `start`,
    without contradicting any already-known cell.

    "Placed starting at `start`" means: first the mandatory gap cells (if
    this isn't the first run) must be EMPTY-compatible, then the run's own
    cells must be FILLED-compatible. Folding the mandatory gap into the
    same placement as the run (rather than handling it as a separate step)
    is what makes the "at least one gap between runs" rule fall out
    automatically, without extra bookkeeping.

    Returns (ok, end): `ok` is whether the placement is valid, and `end` is
    the line position immediately after the run (i.e. where the *next*
    run, or the trailing empty space, would begin).
    """
    prefix = _prefix_gap(run_index)
    length = runs[run_index]
    end = start + prefix + length
    if end > len(current_state):
        return False, end
    for p in range(start, start + prefix):
        if not _compatible(current_state[p], Cell.EMPTY):
            return False, end
    for p in range(start + prefix, end):
        if not _compatible(current_state[p], Cell.FILLED):
            return False, end
    return True, end


def solve_line(clue: Clue, current_state: Line) -> Line:
    """Given a Clue and the current (possibly partial) state of a line, return an
    updated Line with any cells that are certain given all arrangements consistent
    with the clue and already-known cells. Cells that remain ambiguous are left as
    they were (UNKNOWN, or already-known FILLED/EMPTY).

    Raises ContradictionError if no arrangement of the clue is consistent with the
    given line state.
    """
    n = len(current_state)
    runs = list(clue)
    k = len(runs)

    # forward[i][j] = True means: it's possible to fill line[0:i] using
    # exactly the first j runs of the clue (runs[0], ..., runs[j-1]),
    # consistent with whatever is already known in current_state[0:i], and
    # position i is a valid "boundary" — either mid-gap or ready to start
    # run j next. forward[0][0] = True is the base case: an empty prefix
    # trivially satisfies zero runs.
    forward = [[False] * (k + 1) for _ in range(n + 1)]
    forward[0][0] = True

    for i in range(n):
        for j in range(k + 1):
            if not forward[i][j]:
                continue
            # Option 1: treat position i as another EMPTY cell, extending
            # the current gap (this is what allows gaps longer than the
            # bare minimum, and the optional leading/trailing empty space).
            if _compatible(current_state[i], Cell.EMPTY):
                forward[i + 1][j] = True
            # Option 2: place the next run (with its mandatory gap) right
            # here, jumping forward to just past it and incrementing the
            # run count.
            if j < k:
                ok, end = _can_place_run(current_state, i, j, runs)
                if ok:
                    forward[end][j + 1] = True

    # forward[n][k]: is it possible to fill the *entire* line using *all* k
    # runs? If not, no arrangement of this clue fits the known cells at all.
    if not forward[n][k]:
        raise ContradictionError(
            f"No arrangement of {clue!r} is consistent with the given line state"
        )

    # backward[i][j] mirrors forward, but for the suffix: True means it's
    # possible to fill line[i:n] using exactly runs[j:k] (the *remaining*
    # runs from j onward), with position i a valid boundary. Computed by
    # walking the same transitions in reverse, starting from the line's end.
    backward = [[False] * (k + 1) for _ in range(n + 1)]
    backward[n][k] = True

    for i in range(n - 1, -1, -1):
        for j in range(k, -1, -1):
            result = _compatible(current_state[i], Cell.EMPTY) and backward[i + 1][j]
            if not result and j < k:
                ok, end = _can_place_run(current_state, i, j, runs)
                if ok and backward[end][j + 1]:
                    result = True
            backward[i][j] = result

    # Now combine forward and backward: for every boundary (i, j) that's
    # reachable from the start (forward[i][j]) *and* from which the rest of
    # the line can still be completed (backward[...]), record which actual
    # cell values that transition requires. Because at least one full
    # arrangement exists (checked above), every cell is marked possible for
    # at least one of FILLED/EMPTY by the time this loop finishes.
    filled_possible = [False] * n
    empty_possible = [False] * n

    for i in range(n + 1):
        for j in range(k + 1):
            if not forward[i][j]:
                continue
            # This transition treats cell i as EMPTY (part of a gap).
            if i < n and _compatible(current_state[i], Cell.EMPTY) and backward[i + 1][j]:
                empty_possible[i] = True
            # This transition places run j here: its mandatory gap cells
            # are EMPTY, and its own cells are FILLED.
            if j < k:
                ok, end = _can_place_run(current_state, i, j, runs)
                if ok and backward[end][j + 1]:
                    prefix = _prefix_gap(j)
                    for p in range(i, i + prefix):
                        empty_possible[p] = True
                    for p in range(i + prefix, end):
                        filled_possible[p] = True

    # A cell is only "certain" if exactly one of FILLED/EMPTY is possible
    # across every valid arrangement. If both are possible, it's still
    # genuinely ambiguous, so we leave it as it already was (UNKNOWN, or
    # unchanged if it was already known).
    result_cells = []
    for i in range(n):
        if filled_possible[i] and not empty_possible[i]:
            result_cells.append(Cell.FILLED)
        elif empty_possible[i] and not filled_possible[i]:
            result_cells.append(Cell.EMPTY)
        else:
            result_cells.append(current_state[i])

    return Line(result_cells)
