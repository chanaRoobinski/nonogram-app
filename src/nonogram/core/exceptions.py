"""All domain-specific errors raised anywhere in this project, gathered in
one place so any module can import from here without creating circular
dependencies. Each one maps to a specific failure mode; see each class's
docstring for exactly when it's raised and by which module.
"""


class NonogramError(Exception):
    """Base class for all nonogram-specific errors.

    Catch this if you want to handle "anything domain-specific went wrong"
    without catching unrelated Python exceptions (e.g. a real bug elsewhere).
    """


class InvalidClueError(NonogramError, ValueError):
    """Raised by Clue's constructor (core/grid.py) when given a run value
    that isn't a positive integer — e.g. a negative number, a float, or a
    zero embedded in the list (a fully empty line is Clue([]), not
    Clue([0])). Also inherits from ValueError since this is fundamentally a
    "bad value passed in" error."""


class ContradictionError(NonogramError):
    """Raised by the solver (solver/line_solver.py, solver/engine.py) when
    no arrangement of a Clue's runs is consistent with the cells that are
    already known — i.e. the puzzle as given is unsolvable."""


class GenerationTimeoutError(NonogramError):
    """Raised by the puzzle generator (generator/puzzle_generator.py) when
    it exhausts its attempt budget (max_attempts) without finding even one
    valid puzzle — meaning every randomly-generated pattern it tried either
    had no unique solution or was too hard for a human. Note this is
    different from simply not matching the *requested* difficulty exactly:
    generate_puzzle() only raises this if it found no usable puzzle at
    all, returning the closest match it did find otherwise."""
