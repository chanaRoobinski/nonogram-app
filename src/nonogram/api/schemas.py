from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


class GenerateRequest(BaseModel):
    num_rows: int = Field(gt=0)
    num_cols: int = Field(gt=0)
    difficulty: DifficultyLevel
    max_attempts: int = Field(gt=0)
    seed: Optional[int] = None


class DifficultyInfo(BaseModel):
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


class SolveRequest(BaseModel):
    row_clues: list[list[int]]
    col_clues: list[list[int]]
    max_backtrack_depth: Optional[int] = None


class SolveOutcome(str, Enum):
    SOLVED = "SOLVED"
    CONTRADICTION = "CONTRADICTION"
    MAX_DEPTH_EXCEEDED = "MAX_DEPTH_EXCEEDED"


class SolveResponse(BaseModel):
    status: SolveOutcome
    solution: Optional[list[list[bool]]] = None
