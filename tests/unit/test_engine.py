from nonogram.core.grid import Cell, Clue, Grid
from nonogram.solver.engine import SolveStatus, propagate, solve
from tests.fixtures.known_puzzles import CHECKERBOARD_4X4, FRAME_10X10, PLUS_SIGN_5X5

U = Cell.UNKNOWN


class TestPropagate:
    def test_solves_a_propagation_only_puzzle_completely(self):
        blank = Grid.empty(5, 5)
        result, stats = propagate(blank, PLUS_SIGN_5X5.row_clues, PLUS_SIGN_5X5.col_clues)
        assert result == PLUS_SIGN_5X5.solution
        assert stats.lines_solved > 0
        assert stats.cells_deduced == 25

    def test_leaves_ambiguous_cells_unknown(self):
        blank = Grid.empty(4, 4)
        result, _ = propagate(blank, CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues)
        assert any(cell is U for row in result.rows for cell in row)

    def test_empty_dirty_sets_is_a_no_op(self):
        blank = Grid.empty(3, 3)
        row_clues = [Clue([3]), Clue([1]), Clue([3])]
        col_clues = [Clue([3]), Clue([1]), Clue([3])]
        result, stats = propagate(blank, row_clues, col_clues, dirty_rows=set(), dirty_cols=set())
        assert result == blank
        assert stats.lines_solved == 0
        assert stats.cells_deduced == 0


class TestSolve:
    def test_solves_a_propagation_only_puzzle(self):
        blank = Grid.empty(5, 5)
        result = solve(blank, PLUS_SIGN_5X5.row_clues, PLUS_SIGN_5X5.col_clues)
        assert result.status is SolveStatus.SOLVED
        assert result.grid == PLUS_SIGN_5X5.solution
        assert result.stats.max_backtrack_depth == 0
        assert result.stats.guesses == 0

    def test_solves_a_10x10_propagation_only_puzzle(self):
        blank = Grid.empty(10, 10)
        result = solve(blank, FRAME_10X10.row_clues, FRAME_10X10.col_clues)
        assert result.status is SolveStatus.SOLVED
        assert result.grid == FRAME_10X10.solution

    def test_solves_a_puzzle_that_requires_backtracking(self):
        blank = Grid.empty(4, 4)
        result = solve(blank, CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues)
        assert result.status is SolveStatus.SOLVED
        assert result.grid == CHECKERBOARD_4X4.solution
        assert result.stats.max_backtrack_depth >= 1
        assert result.stats.guesses >= 1

    def test_contradictory_clues_report_contradiction_status(self):
        row_clues = [Clue([2]), Clue([2])]
        col_clues = [Clue([1]), Clue([2])]
        result = solve(Grid.empty(2, 2), row_clues, col_clues)
        assert result.status is SolveStatus.CONTRADICTION
        assert result.grid is None

    def test_max_backtrack_depth_reports_max_depth_exceeded(self):
        blank = Grid.empty(4, 4)
        result = solve(
            blank, CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues, max_backtrack_depth=0
        )
        assert result.status is SolveStatus.MAX_DEPTH_EXCEEDED
        assert result.grid is None

    def test_respects_already_known_cells(self):
        rows = [list(row) for row in Grid.empty(5, 5).rows]
        rows[2][2] = Cell.FILLED
        partially_known = Grid(rows)
        result = solve(partially_known, PLUS_SIGN_5X5.row_clues, PLUS_SIGN_5X5.col_clues)
        assert result.status is SolveStatus.SOLVED
        assert result.grid == PLUS_SIGN_5X5.solution

    def test_stats_are_aggregated_across_the_search(self):
        blank = Grid.empty(4, 4)
        result = solve(blank, CHECKERBOARD_4X4.row_clues, CHECKERBOARD_4X4.col_clues)
        assert result.stats.propagation_calls >= 1
        assert result.stats.lines_solved > 0
