"""POST /puzzles/generate — the HTTP wrapper around
generator.puzzle_generator.generate_puzzle(). Translates between the API's
plain-JSON schemas (api/schemas.py) and the richer domain objects
(DifficultyCategory, Clue, ...) the generator actually works with.
"""

from fastapi import APIRouter, HTTPException

from nonogram.api.schemas import DifficultyInfo, DifficultyLevel, GenerateRequest, GenerateResponse
from nonogram.core.exceptions import GenerationTimeoutError
from nonogram.difficulty.evaluator import DifficultyCategory
from nonogram.generator.pattern_source import RandomPatternSource
from nonogram.generator.puzzle_generator import generate_puzzle

router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate a puzzle at the requested size/difficulty.

    Always uses a RandomPatternSource (optionally seeded, for reproducible
    results) — there's no way to submit a hand-built ManualPatternSource
    pattern over HTTP, since that's a testing/internal-tooling concern, not
    something an API client would supply.

    Returns HTTP 422 if generate_puzzle() couldn't find any valid puzzle at
    all within max_attempts (GenerationTimeoutError). Note this is
    different from "didn't hit the exact requested difficulty" — that case
    still returns 200, with exact_match=False in the response.
    """
    requested_category = DifficultyCategory[request.difficulty.value]
    source = RandomPatternSource(seed=request.seed)

    try:
        puzzle = generate_puzzle(
            request.num_rows,
            request.num_cols,
            requested_category,
            request.max_attempts,
            pattern_source=source,
        )
    except GenerationTimeoutError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return GenerateResponse(
        row_clues=[list(clue) for clue in puzzle.row_clues],
        col_clues=[list(clue) for clue in puzzle.col_clues],
        difficulty=DifficultyInfo(
            score=puzzle.difficulty.score,
            category=DifficultyLevel[puzzle.difficulty.category.name],
            suitable_for_human=puzzle.difficulty.suitable_for_human,
        ),
        exact_match=puzzle.exact_match,
    )
