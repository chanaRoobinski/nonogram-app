from dataclasses import dataclass
from enum import Enum, auto

# Above this score, a puzzle is considered beyond reasonable human solving even
# though it's technically "Very Hard" rather than unsolvable. Callers (the
# Stage 6 generator) should treat this as reject-and-retry, not a puzzle to
# hand to a user. User-confirmed threshold, 2026-07-02.
UNSUITABLE_FOR_HUMAN_THRESHOLD = 100


class DifficultyCategory(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    VERY_HARD = auto()


@dataclass
class DifficultyResult:
    score: int
    category: DifficultyCategory
    suitable_for_human: bool


def evaluate_difficulty(solve_stats) -> DifficultyResult:
    """Convert solve statistics (from engine.solve) into a difficulty score and
    category. Propagation alone (lines_solved, cells_deduced_by_propagation)
    contributes nothing to the score — pure logical deduction is always "free".
    Backtracking depth is weighted quadratically since each extra nesting level
    means an exponentially larger search tree; guesses (total branches tried)
    contribute linearly.

    User-confirmed scoring formula and thresholds, 2026-07-02:
        score = guesses + (max_backtrack_depth ** 2) * 5
        Easy = 0, Medium = 1-10, Hard = 11-40, Very Hard = 41+
        suitable_for_human = score <= 100
    """
    score = solve_stats.guesses + (solve_stats.max_backtrack_depth**2) * 5

    if score == 0:
        category = DifficultyCategory.EASY
    elif score <= 10:
        category = DifficultyCategory.MEDIUM
    elif score <= 40:
        category = DifficultyCategory.HARD
    else:
        category = DifficultyCategory.VERY_HARD

    suitable_for_human = score <= UNSUITABLE_FOR_HUMAN_THRESHOLD

    return DifficultyResult(score=score, category=category, suitable_for_human=suitable_for_human)
