import pytest

from nonogram.core.exceptions import ContradictionError
from nonogram.core.grid import Cell, Clue, Line
from nonogram.solver.line_solver import solve_line

U, F, E = Cell.UNKNOWN, Cell.FILLED, Cell.EMPTY


def test_basic_overlap_resolves_only_the_guaranteed_cell():
    # clue [3] on a line of length 5: starts 0..2 all cover index 2, nothing else.
    result = solve_line(Clue([3]), Line([U, U, U, U, U]))
    assert result == Line([U, U, F, U, U])


def test_partial_overlap_only_does_not_fully_solve_the_line():
    # Same as above: only one of five cells becomes certain — the rest stay UNKNOWN.
    result = solve_line(Clue([3]), Line([U, U, U, U, U]))
    assert result.cells.count(U) == 4
    assert result.cells.count(F) == 1


def test_run_equal_to_line_length_fills_everything():
    result = solve_line(Clue([5]), Line([U, U, U, U, U]))
    assert result == Line([F, F, F, F, F])


def test_empty_clue_forces_entire_line_empty():
    result = solve_line(Clue([]), Line([U, U, U]))
    assert result == Line([E, E, E])


def test_empty_clue_on_zero_length_line():
    result = solve_line(Clue([]), Line([]))
    assert result == Line([])


def test_empty_clue_contradicts_a_known_filled_cell():
    with pytest.raises(ContradictionError):
        solve_line(Clue([]), Line([E, F, E]))


def test_clue_that_cannot_fit_raises_contradiction():
    with pytest.raises(ContradictionError):
        solve_line(Clue([5]), Line([U, U, U]))


def test_nonempty_clue_on_zero_length_line_raises_contradiction():
    with pytest.raises(ContradictionError):
        solve_line(Clue([1]), Line([]))


def test_already_fully_known_consistent_line_is_unchanged():
    line = Line([F, F, E, F])
    assert solve_line(Clue([2, 1]), line) == line


def test_already_fully_known_inconsistent_line_raises_contradiction():
    with pytest.raises(ContradictionError):
        solve_line(Clue([2, 1]), Line([F, E, E, F]))


def test_known_cell_forces_run_position():
    # clue [2] on length 4, with index 3 known FILLED: the only placement
    # covering index 3 is start=2, so index 2 is also forced FILLED and index
    # 0 and 1 are forced EMPTY.
    result = solve_line(Clue([2]), Line([U, U, U, F]))
    assert result == Line([E, E, F, F])


def test_multi_run_with_trailing_known_empty():
    # clue [2, 1] on length 6 with the last cell known EMPTY removes any
    # placement that would need the final run to sit at the very end.
    result = solve_line(Clue([2, 1]), Line([U, U, U, U, U, E]))
    assert result[5] == E


def test_mandatory_gap_between_runs_is_enforced():
    # clue [1, 1] on length 2 is infeasible: two runs of 1 need at least one
    # gap cell between them, which doesn't fit in a line of length 2.
    with pytest.raises(ContradictionError):
        solve_line(Clue([1, 1]), Line([U, U]))
