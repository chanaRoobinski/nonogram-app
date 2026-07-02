from dataclasses import dataclass

from nonogram.core.exceptions import GenerationTimeoutError
from nonogram.core.grid import Grid
from nonogram.difficulty.evaluator import DifficultyCategory, DifficultyResult, evaluate_difficulty
from nonogram.generator.pattern_source import PatternSource, RandomPatternSource, extract_clues
from nonogram.solver.engine import solve
from nonogram.solver.uniqueness import has_unique_solution

_CATEGORY_ORDER = list(DifficultyCategory)


@dataclass
class Puzzle:
    solution: Grid
    row_clues: list
    col_clues: list
    difficulty: DifficultyResult
    found_at_attempt: int
    exact_match: bool


def _category_distance(a, b):
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

        if not has_unique_solution(row_clues, col_clues, max_backtrack_depth):
            continue

        # has_unique_solution() above already confirmed a solution exists, so
        # this is always SolveStatus.SOLVED.
        result = solve(Grid.empty(num_rows, num_cols), row_clues, col_clues, max_backtrack_depth)
        difficulty = evaluate_difficulty(result.stats)
        if not difficulty.suitable_for_human:
            continue

        exact_match = difficulty.category is requested_category
        candidate = Puzzle(pattern, row_clues, col_clues, difficulty, attempt, exact_match)

        if exact_match:
            return candidate

        if best is None or _category_distance(
            difficulty.category, requested_category
        ) < _category_distance(best.difficulty.category, requested_category):
            best = candidate

    if best is not None:
        return best

    raise GenerationTimeoutError(
        f"No valid unique-solution puzzle found within {max_attempts} attempts"
    )
