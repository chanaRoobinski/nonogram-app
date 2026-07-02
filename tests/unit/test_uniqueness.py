from nonogram.core.grid import Clue
from nonogram.solver.uniqueness import check_uniqueness, has_unique_solution
from tests.fixtures.known_puzzles import CHECKERBOARD_4X4, PLUS_SIGN_5X5


def test_puzzle_solvable_by_propagation_alone_is_unique():
    # Any puzzle fully resolved by pure constraint propagation is provably
    # unique: every cell was logically forced, not guessed.
    assert has_unique_solution(PLUS_SIGN_5X5.row_clues, PLUS_SIGN_5X5.col_clues) is True


def test_deliberately_ambiguous_puzzle_is_not_unique():
    # Every row/column clue is [1, 1] on a 4x4 board: the checkerboard and its
    # complement (inverted checkerboard) both satisfy every clue.
    assert has_unique_solution(CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues) is False


def test_unsolvable_puzzle_is_not_unique():
    row_clues = [Clue([2]), Clue([2])]
    col_clues = [Clue([1]), Clue([2])]
    assert has_unique_solution(row_clues, col_clues) is False


class TestCheckUniqueness:
    def test_unique_puzzle_reports_first_solution_and_no_alternate(self):
        result = check_uniqueness(PLUS_SIGN_5X5.row_clues, PLUS_SIGN_5X5.col_clues)
        assert result.is_unique is True
        assert result.first_solution == PLUS_SIGN_5X5.solution
        assert result.alternate_solution is None

    def test_ambiguous_puzzle_reports_a_genuinely_different_alternate(self):
        result = check_uniqueness(CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues)
        assert result.is_unique is False
        assert result.first_solution is not None
        assert result.alternate_solution is not None
        assert result.alternate_solution != result.first_solution

    def test_unsolvable_puzzle_reports_no_solutions_at_all(self):
        row_clues = [Clue([2]), Clue([2])]
        col_clues = [Clue([1]), Clue([2])]
        result = check_uniqueness(row_clues, col_clues)
        assert result.is_unique is False
        assert result.first_solution is None
        assert result.alternate_solution is None
