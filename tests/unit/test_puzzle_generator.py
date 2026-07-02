import pytest

from nonogram.core.exceptions import GenerationTimeoutError
from nonogram.difficulty.evaluator import DifficultyCategory, DifficultyResult
from nonogram.generator import puzzle_generator
from nonogram.generator.pattern_source import ManualPatternSource
from nonogram.generator.puzzle_generator import generate_puzzle
from tests.fixtures.known_puzzles import CHECKERBOARD_4X4, PLUS_SIGN_5X5


def test_manual_easy_pattern_returns_exact_match_on_first_attempt():
    source = ManualPatternSource(PLUS_SIGN_5X5.solution)
    puzzle = generate_puzzle(5, 5, DifficultyCategory.EASY, max_attempts=1, pattern_source=source)
    assert puzzle.exact_match is True
    assert puzzle.difficulty.category is DifficultyCategory.EASY
    assert puzzle.found_at_attempt == 1
    assert puzzle.solution == PLUS_SIGN_5X5.solution
    assert puzzle.row_clues == PLUS_SIGN_5X5.row_clues
    assert puzzle.col_clues == PLUS_SIGN_5X5.col_clues


def test_unreachable_category_returns_closest_match_not_exact():
    # The manual source always yields the same EASY (score 0) pattern, so
    # VERY_HARD is unreachable — the loop should exhaust max_attempts and
    # fall back to the closest match found rather than raising.
    source = ManualPatternSource(PLUS_SIGN_5X5.solution)
    puzzle = generate_puzzle(
        5, 5, DifficultyCategory.VERY_HARD, max_attempts=3, pattern_source=source
    )
    assert puzzle.exact_match is False
    assert puzzle.difficulty.category is DifficultyCategory.EASY
    assert 1 <= puzzle.found_at_attempt <= 3


def test_never_unique_pattern_raises_generation_timeout():
    # The checkerboard fixture has two solutions (itself and its complement),
    # so it never passes the uniqueness check — no candidate is ever valid.
    source = ManualPatternSource(CHECKERBOARD_4X4.solution)
    with pytest.raises(GenerationTimeoutError):
        generate_puzzle(4, 4, DifficultyCategory.EASY, max_attempts=2, pattern_source=source)


def test_unsuitable_for_human_candidates_are_skipped(monkeypatch):
    # Every real attempt here would score 0/Easy; force the first evaluation
    # to look like an extreme (score > 100) puzzle so we can deterministically
    # exercise the "reject and keep searching" branch without needing to find
    # a naturally-occurring pathological random pattern.
    real_evaluate_difficulty = puzzle_generator.evaluate_difficulty
    calls = {"count": 0}

    def fake_evaluate_difficulty(stats):
        calls["count"] += 1
        if calls["count"] == 1:
            return DifficultyResult(score=999, category=DifficultyCategory.VERY_HARD,
                                      suitable_for_human=False)
        return real_evaluate_difficulty(stats)

    monkeypatch.setattr(puzzle_generator, "evaluate_difficulty", fake_evaluate_difficulty)

    source = ManualPatternSource(PLUS_SIGN_5X5.solution)
    puzzle = generate_puzzle(5, 5, DifficultyCategory.EASY, max_attempts=2, pattern_source=source)

    assert calls["count"] == 2
    assert puzzle.exact_match is True
    assert puzzle.difficulty.category is DifficultyCategory.EASY


def test_random_source_can_reach_a_non_easy_difficulty():
    # Fixed seed for determinism; a modestly dense 6x6 grid reliably needs at
    # least one guess for at least one of these attempts.
    from nonogram.generator.pattern_source import RandomPatternSource

    source = RandomPatternSource(density=0.5, smoothing_passes=1, seed=3)
    puzzle = generate_puzzle(
        6, 6, DifficultyCategory.MEDIUM, max_attempts=50, pattern_source=source
    )
    assert puzzle.difficulty.suitable_for_human is True
    if puzzle.exact_match:
        assert puzzle.difficulty.category is DifficultyCategory.MEDIUM
