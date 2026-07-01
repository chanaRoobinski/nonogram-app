from nonogram.core.exceptions import ContradictionError
from nonogram.core.grid import Cell, Clue, Line


def _compatible(cell: Cell, value: Cell) -> bool:
    return cell is Cell.UNKNOWN or cell is value


def _prefix_gap(run_index: int) -> int:
    """Mandatory gap cells required before this run (none before the first run)."""
    return 1 if run_index > 0 else 0


def _can_place_run(current_state: Line, start: int, run_index: int, runs: list) -> tuple:
    """Check whether run `run_index` can be placed with its mandatory gap starting at
    `start`. Returns (ok, end) where `end` is the boundary position just past the run."""
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

    # forward[i][j]: line[0:i] can be filled using exactly runs[0:j], consistent
    # with current_state[0:i], with position i a valid boundary (start of a gap or
    # the next run).
    forward = [[False] * (k + 1) for _ in range(n + 1)]
    forward[0][0] = True

    for i in range(n):
        for j in range(k + 1):
            if not forward[i][j]:
                continue
            if _compatible(current_state[i], Cell.EMPTY):
                forward[i + 1][j] = True
            if j < k:
                ok, end = _can_place_run(current_state, i, j, runs)
                if ok:
                    forward[end][j + 1] = True

    if not forward[n][k]:
        raise ContradictionError(
            f"No arrangement of {clue!r} is consistent with the given line state"
        )

    # backward[i][j]: line[i:n] can be filled using exactly runs[j:k], consistent
    # with current_state[i:n], with position i a valid boundary.
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

    filled_possible = [False] * n
    empty_possible = [False] * n

    for i in range(n + 1):
        for j in range(k + 1):
            if not forward[i][j]:
                continue
            if i < n and _compatible(current_state[i], Cell.EMPTY) and backward[i + 1][j]:
                empty_possible[i] = True
            if j < k:
                ok, end = _can_place_run(current_state, i, j, runs)
                if ok and backward[end][j + 1]:
                    prefix = _prefix_gap(j)
                    for p in range(i, i + prefix):
                        empty_possible[p] = True
                    for p in range(i + prefix, end):
                        filled_possible[p] = True

    result_cells = []
    for i in range(n):
        if filled_possible[i] and not empty_possible[i]:
            result_cells.append(Cell.FILLED)
        elif empty_possible[i] and not filled_possible[i]:
            result_cells.append(Cell.EMPTY)
        else:
            result_cells.append(current_state[i])

    return Line(result_cells)
