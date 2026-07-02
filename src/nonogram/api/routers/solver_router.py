from fastapi import APIRouter, HTTPException

from nonogram.api.schemas import SolveOutcome, SolveRequest, SolveResponse
from nonogram.core.exceptions import InvalidClueError
from nonogram.core.grid import Cell, Clue, Grid
from nonogram.solver.engine import solve

router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("/solve", response_model=SolveResponse)
def solve_puzzle(request: SolveRequest) -> SolveResponse:
    try:
        row_clues = [Clue(runs) for runs in request.row_clues]
        col_clues = [Clue(runs) for runs in request.col_clues]
    except InvalidClueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    blank = Grid.empty(len(row_clues), len(col_clues))
    result = solve(blank, row_clues, col_clues, request.max_backtrack_depth)

    solution = None
    if result.grid is not None:
        solution = [[cell is Cell.FILLED for cell in row] for row in result.grid.rows]

    return SolveResponse(status=SolveOutcome[result.status.name], solution=solution)
