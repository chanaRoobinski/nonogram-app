import pytest

from nonogram.core.grid import Grid
from nonogram.difficulty.evaluator import DifficultyCategory, evaluate_difficulty
from nonogram.generator.pattern_source import RandomPatternSource
from nonogram.generator.puzzle_generator import generate_puzzle
from nonogram.solver.engine import SolveStatus, solve
from nonogram.solver.uniqueness import has_unique_solution
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


class TestPuzzleGenerationEndToEnd:
    """Stage 6: requesting a puzzle at a given difficulty actually returns one
    evaluated at that difficulty, with a unique solution. Fixed seed so this
    is deterministic."""

    @pytest.mark.parametrize("category", [DifficultyCategory.EASY, DifficultyCategory.MEDIUM])
    def test_requested_difficulty_is_reached_with_a_unique_solution(self, category):
        source = RandomPatternSource(density=0.45, smoothing_passes=2, seed=42)
        puzzle = generate_puzzle(10, 10, category, max_attempts=20, pattern_source=source)

        assert puzzle.exact_match is True
        assert puzzle.difficulty.category is category
        assert has_unique_solution(puzzle.row_clues, puzzle.col_clues) is True
