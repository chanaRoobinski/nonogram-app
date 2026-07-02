import random
import time

from nonogram.core.grid import Cell, Grid
from nonogram.generator.pattern_source import extract_clues, line_clue
from nonogram.solver.engine import SolveStatus, solve
from tests.fixtures.known_puzzles import ALL_KNOWN_PUZZLES


def _random_solved_grid(rows, cols, density, seed):
    rng = random.Random(seed)
    cells = [
        [Cell.FILLED if rng.random() < density else Cell.EMPTY for _ in range(cols)]
        for _ in range(rows)
    ]
    return Grid(cells)


class TestKnownPuzzlesPipeline:
    def test_all_known_puzzles_solve_to_their_recorded_solution(self):
        for puzzle in ALL_KNOWN_PUZZLES:
            blank = Grid.empty(puzzle.solution.num_rows, puzzle.solution.num_cols)
            result = solve(blank, puzzle.row_clues, puzzle.col_clues)
            assert result.status is SolveStatus.SOLVED, puzzle.name
            assert result.grid == puzzle.solution, puzzle.name


class TestPerformanceBaseline:
    def test_20x20_grid_solves_within_a_generous_time_budget(self):
        # A random grid isn't guaranteed to have a *unique* solution, so we only
        # check that the solver's answer is *valid* (matches the clues it was
        # given), not that it's byte-for-byte the grid we happened to generate.
        seed_solution = _random_solved_grid(20, 20, density=0.45, seed=42)
        row_clues, col_clues = extract_clues(seed_solution)
        blank = Grid.empty(20, 20)

        start = time.perf_counter()
        result = solve(blank, row_clues, col_clues)
        duration = time.perf_counter() - start

        assert result.status is SolveStatus.SOLVED
        assert [line_clue(row) for row in result.grid.rows] == row_clues
        assert [line_clue(col) for col in result.grid.columns] == col_clues
        # Baseline only, not a strict perf contract (per skill Stage 3) — a
        # generous ceiling that only trips on a catastrophic regression.
        assert duration < 30
