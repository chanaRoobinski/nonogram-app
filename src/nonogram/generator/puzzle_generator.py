"""The top-level "give me a puzzle of this size and difficulty" entry point,
tying together every other package: it draws candidate patterns from a
PatternSource, filters them through the uniqueness check (solver/uniqueness.py)
and the solver (solver/engine.py), scores them with the difficulty evaluator
(difficulty/evaluator.py), and returns the first one that matches what was
asked for.
"""

from dataclasses import dataclass

from nonogram.core.exceptions import GenerationTimeoutError
from nonogram.core.grid import Grid
from nonogram.difficulty.evaluator import DifficultyCategory, DifficultyResult, evaluate_difficulty
from nonogram.generator.pattern_source import PatternSource, RandomPatternSource, extract_clues
from nonogram.solver.engine import solve
from nonogram.solver.uniqueness import has_unique_solution

# DifficultyCategory members are declared EASY < MEDIUM < HARD < VERY_HARD;
# this list captures that order so "how many tiers apart are two
# categories?" can be answered by comparing list positions.
_CATEGORY_ORDER = list(DifficultyCategory)


@dataclass
class Puzzle:
    """A generated puzzle, ready to be handed to a player (via row_clues/
    col_clues) or inspected for testing/debugging (via solution)."""

    solution: Grid
    """The fully-solved pattern this puzzle was generated from — not shown
    to players, only used internally and by tests."""

    row_clues: list
    """The Clue for each row, in order — what a player actually sees."""

    col_clues: list
    """The Clue for each column, in order — what a player actually sees."""

    difficulty: DifficultyResult
    """How hard this puzzle actually turned out to be, per evaluate_difficulty()."""

    found_at_attempt: int
    """Which attempt (1-based) of the generate-and-test loop produced this
    puzzle. Note this reflects when *this* candidate was found, not
    necessarily how many attempts the whole generate_puzzle() call made in
    total — if this is a fallback "closest match" result, more attempts may
    have run afterward looking for (and failing to find) an exact match."""

    exact_match: bool
    """True if difficulty.category is exactly the category that was
    requested. False means this is the closest match found once
    max_attempts ran out — still a valid, unique, human-suitable puzzle,
    just not at precisely the requested difficulty."""


def _category_distance(a, b):
    """How many difficulty tiers apart two categories are (0 if equal, 1 for
    adjacent tiers like MEDIUM/HARD, etc.) — used to pick the "closest"
    fallback candidate when no exact match is found."""
    return abs(_CATEGORY_ORDER.index(a) - _CATEGORY_ORDER.index(b))


def generate_puzzle(
    num_rows,
    num_cols,
    requested_category,
    max_attempts,
    pattern_source: PatternSource = None,
    max_backtrack_depth=None,
) -> Puzzle:
    """Generate-and-test loop targeting a requested difficulty: repeatedly
    draw a pattern, keep it only if it has a unique solution and is suitable
    for a human (Stage 5's suitable_for_human), score its difficulty, and
    return as soon as one matches requested_category.

    If max_attempts is exhausted without an exact match, returns the closest
    match found so far with Puzzle.exact_match=False, rather than failing —
    the requested difficulty may simply be unreachable at this size. Raises
    GenerationTimeoutError only if no valid puzzle was found at all.
    """
    source = pattern_source or RandomPatternSource()
    best = None

    for attempt in range(1, max_attempts + 1):
        pattern = source.generate(num_rows, num_cols)
        row_clues, col_clues = extract_clues(pattern)

        # Reject patterns whose clues could be satisfied by more than one
        # solution — a real puzzle needs exactly one right answer.
        if not has_unique_solution(row_clues, col_clues, max_backtrack_depth):
            continue

        # has_unique_solution() above already confirmed a solution exists, so
        # this is always SolveStatus.SOLVED.
        result = solve(Grid.empty(num_rows, num_cols), row_clues, col_clues, max_backtrack_depth)
        difficulty = evaluate_difficulty(result.stats)
        # Reject patterns that are technically solvable but too hard for a
        # person to reasonably attempt (see difficulty/evaluator.py).
        if not difficulty.suitable_for_human:
            continue

        exact_match = difficulty.category is requested_category
        candidate = Puzzle(pattern, row_clues, col_clues, difficulty, attempt, exact_match)

        if exact_match:
            return candidate

        # Not an exact match, but keep it around as a fallback if it's
        # closer to the requested difficulty than anything found so far.
        if best is None or _category_distance(
            difficulty.category, requested_category
        ) < _category_distance(best.difficulty.category, requested_category):
            best = candidate

    if best is not None:
        return best

    raise GenerationTimeoutError(
        f"No valid unique-solution puzzle found within {max_attempts} attempts"
    )
