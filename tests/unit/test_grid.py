import pytest

from nonogram.core.exceptions import InvalidClueError
from nonogram.core.grid import Cell, Clue, Grid, Line


class TestClue:
    def test_valid_clue_stores_runs(self):
        assert Clue([3, 1]).runs == (3, 1)

    def test_empty_clue_is_valid(self):
        clue = Clue([])
        assert len(clue) == 0
        assert list(clue) == []

    def test_zero_run_is_invalid(self):
        with pytest.raises(InvalidClueError):
            Clue([0, 3])

    def test_negative_run_is_invalid(self):
        with pytest.raises(InvalidClueError):
            Clue([-1])

    def test_non_integer_run_is_invalid(self):
        with pytest.raises(InvalidClueError):
            Clue([1.5])

    def test_bool_run_is_invalid(self):
        with pytest.raises(InvalidClueError):
            Clue([True])

    def test_equality(self):
        assert Clue([3, 1]) == Clue([3, 1])
        assert Clue([3, 1]) != Clue([1, 3])
        assert Clue([3, 1]) != "not a clue"

    def test_indexing_and_iteration(self):
        clue = Clue([3, 1, 2])
        assert clue[0] == 3
        assert list(clue) == [3, 1, 2]

    def test_hashable(self):
        assert hash(Clue([3, 1])) == hash(Clue([3, 1]))

    def test_repr(self):
        assert repr(Clue([3, 1])) == "Clue([3, 1])"


class TestLine:
    def test_unknown_line_has_correct_length_and_cells(self):
        line = Line.unknown(5)
        assert len(line) == 5
        assert all(cell is Cell.UNKNOWN for cell in line)

    def test_invalid_cell_type_raises(self):
        with pytest.raises(TypeError):
            Line([Cell.FILLED, "not a cell"])

    def test_equality(self):
        assert Line([Cell.FILLED, Cell.EMPTY]) == Line([Cell.FILLED, Cell.EMPTY])
        assert Line([Cell.FILLED]) != Line([Cell.EMPTY])

    def test_indexing_and_iteration(self):
        line = Line([Cell.FILLED, Cell.EMPTY, Cell.UNKNOWN])
        assert line[1] is Cell.EMPTY
        assert list(line) == [Cell.FILLED, Cell.EMPTY, Cell.UNKNOWN]

    def test_hashable(self):
        assert hash(Line([Cell.FILLED])) == hash(Line([Cell.FILLED]))

    def test_repr(self):
        assert repr(Line([Cell.FILLED])) == "Line([<Cell.FILLED: 2>])"

    def test_not_equal_to_non_line(self):
        assert Line([Cell.FILLED]) != "not a line"


class TestGrid:
    def test_empty_grid_has_correct_dimensions(self):
        grid = Grid.empty(3, 4)
        assert grid.num_rows == 3
        assert grid.num_cols == 4

    def test_grid_with_zero_rows_has_zero_cols(self):
        grid = Grid([])
        assert grid.num_rows == 0
        assert grid.num_cols == 0

    def test_mismatched_row_lengths_raise(self):
        with pytest.raises(ValueError):
            Grid([Line.unknown(3), Line.unknown(4)])

    def test_row_access(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        assert grid.row(0) == Line([Cell.FILLED, Cell.EMPTY])
        assert grid.row(1) == Line([Cell.EMPTY, Cell.FILLED])

    def test_column_access(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        assert grid.column(0) == Line([Cell.FILLED, Cell.EMPTY])
        assert grid.column(1) == Line([Cell.EMPTY, Cell.FILLED])

    def test_transpose_row_equals_original_column(self):
        grid = Grid(
            [
                [Cell.FILLED, Cell.EMPTY, Cell.UNKNOWN],
                [Cell.EMPTY, Cell.FILLED, Cell.FILLED],
                [Cell.UNKNOWN, Cell.UNKNOWN, Cell.EMPTY],
            ]
        )
        transposed = grid.transpose()
        for i in range(grid.num_cols):
            assert transposed.row(i) == grid.column(i)

    def test_double_transpose_equals_original(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        assert grid.transpose().transpose() == grid

    def test_equality(self):
        grid_a = Grid([[Cell.FILLED, Cell.EMPTY]])
        grid_b = Grid([[Cell.FILLED, Cell.EMPTY]])
        grid_c = Grid([[Cell.EMPTY, Cell.FILLED]])
        assert grid_a == grid_b
        assert grid_a != grid_c
        assert grid_a != "not a grid"

    def test_rows_property(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        assert grid.rows == (
            Line([Cell.FILLED, Cell.EMPTY]),
            Line([Cell.EMPTY, Cell.FILLED]),
        )

    def test_columns_property(self):
        grid = Grid([[Cell.FILLED, Cell.EMPTY], [Cell.EMPTY, Cell.FILLED]])
        assert grid.columns == (
            Line([Cell.FILLED, Cell.EMPTY]),
            Line([Cell.EMPTY, Cell.FILLED]),
        )

    def test_repr(self):
        grid = Grid([[Cell.FILLED]])
        assert "Grid(" in repr(grid)
