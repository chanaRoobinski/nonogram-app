from fastapi import APIRouter, HTTPException

from nonogram.api.schemas import DifficultyInfo, DifficultyLevel, GenerateRequest, GenerateResponse
from nonogram.core.exceptions import GenerationTimeoutError
from nonogram.difficulty.evaluator import DifficultyCategory
from nonogram.generator.pattern_source import RandomPatternSource
from nonogram.generator.puzzle_generator import generate_puzzle

router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
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
