"""Pydantic request/response models for the API (api/main.py, api/routers/).
These are the JSON "shape" a client sends and receives — the routers
translate between these plain-data models and the richer domain objects
(Clue, Grid, DifficultyCategory, ...) used everywhere else in the codebase.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """The JSON-friendly mirror of difficulty.evaluator.DifficultyCategory
    — a plain string enum so it serializes cleanly to/from JSON. Values are
    named identically to DifficultyCategory's members so converting between
    the two is just a name lookup (see the routers)."""

    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


class GenerateRequest(BaseModel):
    """Body of POST /puzzles/generate."""

    num_rows: int = Field(gt=0)
    num_cols: int = Field(gt=0)
    difficulty: DifficultyLevel
    max_attempts: int = Field(gt=0)
    seed: Optional[int] = None
    """Optional random seed for reproducible generation — the same seed
    with the same other parameters always produces the same puzzle."""


class DifficultyInfo(BaseModel):
    """The difficulty portion of a GenerateResponse — mirrors
    difficulty.evaluator.DifficultyResult."""

    score: int
    category: DifficultyLevel
    suitable_for_human: bool


class GenerateResponse(BaseModel):
    """Deliberately excludes the solution grid: the frontend renders the
    puzzle from the clues alone and validates a player's attempt via
    POST /puzzles/solve, rather than receiving the answer up front."""

    row_clues: list[list[int]]
    col_clues: list[list[int]]
    difficulty: DifficultyInfo
    exact_match: bool
    """True if a puzzle matching the exact requested difficulty was found;
    False if this is the closest match generate_puzzle() could produce
    within its attempt budget (see generator/puzzle_generator.py)."""


class SolveRequest(BaseModel):
    """Body of POST /puzzles/solve. row_clues/col_clues are plain lists of
    run-length lists (e.g. [[3, 1], [2]]) — the JSON equivalent of a list of
    core.grid.Clue objects."""

    row_clues: list[list[int]]
    col_clues: list[list[int]]
    max_backtrack_depth: Optional[int] = None
    """Optional cap on backtracking depth — see solver.engine.solve. Left
    unset (None) for no limit."""


class SolveOutcome(str, Enum):
    """The JSON-friendly mirror of solver.engine.SolveStatus."""

    SOLVED = "SOLVED"
    CONTRADICTION = "CONTRADICTION"
    MAX_DEPTH_EXCEEDED = "MAX_DEPTH_EXCEEDED"


class SolveResponse(BaseModel):
    """Response of POST /puzzles/solve."""

    status: SolveOutcome
    solution: Optional[list[list[bool]]] = None
    """The solved grid as rows of booleans (True = filled), present only
    when status is SOLVED."""
