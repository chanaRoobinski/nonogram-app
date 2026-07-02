import pytest

from nonogram.core.grid import Cell, Grid
from nonogram.generator.pattern_source import (
    ManualPatternSource,
    RandomPatternSource,
    extract_clues,
    line_clue,
)


class TestRandomPatternSource:
    def test_generates_correct_dimensions_with_no_unknown_cells(self):
        pattern = RandomPatternSource(seed=1).generate(6, 8)
        assert pattern.num_rows == 6
        assert pattern.num_cols == 8
        assert all(cell is not Cell.UNKNOWN for row in pattern.rows for cell in row)

    def test_same_seed_is_deterministic(self):
        a = RandomPatternSource(seed=7).generate(5, 5)
        b = RandomPatternSource(seed=7).generate(5, 5)
        assert a == b

    def test_successive_calls_from_one_source_differ(self):
        source = RandomPatternSource(seed=7)
        first = source.generate(6, 6)
        second = source.generate(6, 6)
        assert first != second


class TestManualPatternSource:
    def test_returns_the_wrapped_grid(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        source = ManualPatternSource(grid)
        assert source.generate(2, 2) == grid

    def test_dimension_mismatch_raises(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY]])
        source = ManualPatternSource(grid)
        with pytest.raises(ValueError):
            source.generate(2, 2)


class TestLineClue:
    def test_empty_line(self):
        assert line_clue([Cell.EMPTY, Cell.EMPTY]).runs == ()

    def test_single_run(self):
        assert line_clue([Cell.EMPTY, Cell.FILLED, Cell.FILLED, Cell.EMPTY]).runs == (2,)

    def test_multiple_runs(self):
        cells = [Cell.FILLED, Cell.EMPTY, Cell.FILLED, Cell.FILLED, Cell.EMPTY, Cell.FILLED]
        assert line_clue(cells).runs == (1, 2, 1)

    def test_fully_filled_line(self):
        assert line_clue([Cell.FILLED] * 4).runs == (4,)


class TestExtractClues:
    def test_matches_hand_computed_clues(self):
        pattern = Grid(
            [
                [Cell.FILLED, Cell.EMPTY, Cell.FILLED],
                [Cell.EMPTY, Cell.FILLED, Cell.EMPTY],
                [Cell.FILLED, Cell.FILLED, Cell.FILLED],
            ]
        )
        row_clues, col_clues = extract_clues(pattern)
        assert [c.runs for c in row_clues] == [(1, 1), (1,), (3,)]
        assert [c.runs for c in col_clues] == [(1, 1), (2,), (1, 1)]
