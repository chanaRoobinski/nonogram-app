class NonogramError(Exception):
    """Base class for all nonogram-specific errors."""


class InvalidClueError(NonogramError, ValueError):
    """Raised when a Clue is constructed with invalid run values."""


class ContradictionError(NonogramError):
    """Raised by the solver when no arrangement satisfies the given constraints."""


class GenerationTimeoutError(NonogramError):
    """Raised when the puzzle generator exhausts its attempt budget without
    finding any valid (unique-solution, human-suitable) puzzle at all."""
