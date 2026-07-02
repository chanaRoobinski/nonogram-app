import pytest

from nonogram.difficulty.evaluator import DifficultyCategory, evaluate_difficulty
from nonogram.solver.engine import SolveStats


@pytest.mark.parametrize(
    "guesses,max_backtrack_depth,expected_score,expected_category",
    [
        (0, 0, 0, DifficultyCategory.EASY),
        (1, 0, 1, DifficultyCategory.MEDIUM),
        (10, 0, 10, DifficultyCategory.MEDIUM),
        (11, 0, 11, DifficultyCategory.HARD),
        (0, 2, 20, DifficultyCategory.HARD),
        (0, 3, 45, DifficultyCategory.VERY_HARD),
        (40, 0, 40, DifficultyCategory.HARD),
        (41, 0, 41, DifficultyCategory.VERY_HARD),
    ],
)
def test_score_and_category(guesses, max_backtrack_depth, expected_score, expected_category):
    stats = SolveStats(guesses=guesses, max_backtrack_depth=max_backtrack_depth)
    result = evaluate_difficulty(stats)
    assert result.score == expected_score
    assert result.category is expected_category


def test_score_exactly_at_reject_threshold_is_suitable():
    # depth=4 -> 16*5=80, +20 guesses = 100
    stats = SolveStats(guesses=20, max_backtrack_depth=4)
    result = evaluate_difficulty(stats)
    assert result.score == 100
    assert result.suitable_for_human is True
    assert result.category is DifficultyCategory.VERY_HARD


def test_score_just_over_reject_threshold_is_unsuitable():
    stats = SolveStats(guesses=21, max_backtrack_depth=4)
    result = evaluate_difficulty(stats)
    assert result.score == 101
    assert result.suitable_for_human is False


def test_pure_propagation_is_always_suitable_and_easy():
    stats = SolveStats(
        propagation_calls=3, lines_solved=10, cells_deduced_by_propagation=25, guesses=0,
        max_backtrack_depth=0,
    )
    result = evaluate_difficulty(stats)
    assert result.category is DifficultyCategory.EASY
    assert result.suitable_for_human is True
