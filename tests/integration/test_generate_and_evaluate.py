from nonogram.core.grid import Grid
from nonogram.difficulty.evaluator import DifficultyCategory, evaluate_difficulty
from nonogram.solver.engine import SolveStatus, solve
from tests.fixtures.known_puzzles import CHECKERBOARD_4X4, FRAME_10X10, PLUS_SIGN_5X5


def _solve_and_evaluate(puzzle):
    blank = Grid.empty(puzzle.solution.num_rows, puzzle.solution.num_cols)
    result = solve(blank, puzzle.row_clues, puzzle.col_clues)
    assert result.status is SolveStatus.SOLVED
    return evaluate_difficulty(result.stats)


def test_propagation_only_puzzles_are_easy():
    for puzzle in (PLUS_SIGN_5X5, FRAME_10X10):
        difficulty = _solve_and_evaluate(puzzle)
        assert difficulty.category is DifficultyCategory.EASY, puzzle.name
        assert difficulty.score == 0
        assert difficulty.suitable_for_human is True


def test_puzzle_requiring_backtracking_is_not_easy():
    difficulty = _solve_and_evaluate(CHECKERBOARD_4X4)
    assert difficulty.category is not DifficultyCategory.EASY
    assert difficulty.score > 0
