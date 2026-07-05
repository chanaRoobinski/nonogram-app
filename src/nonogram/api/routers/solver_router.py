"""POST /puzzles/solve — the HTTP wrapper around solver.engine.solve(). Lets
a frontend fetch the correct solution for a given set of clues, e.g. to
validate a player's in-progress attempt (by comparing against what this
endpoint returns) without the frontend needing its own solving logic.
"""

from fastapi import APIRouter, HTTPException

from nonogram.api.schemas import SolveOutcome, SolveRequest, SolveResponse
from nonogram.core.exceptions import InvalidClueError
from nonogram.core.grid import Cell, Clue, Grid
from nonogram.solver.engine import solve

router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("/solve", response_model=SolveResponse)
def solve_puzzle(request: SolveRequest) -> SolveResponse:
    """Solve the given row/column clues from a blank grid.

    Returns HTTP 422 if any clue's run values are invalid (e.g. negative —
    InvalidClueError). Otherwise always returns 200, with `status`
    reflecting whatever solver.engine.solve() reported (SOLVED,
    CONTRADICTION, or MAX_DEPTH_EXCEEDED) — a puzzle with no solution is a
    normal, expected outcome for this endpoint, not a client error.
    """
    try:
        row_clues = [Clue(runs) for runs in request.row_clues]
        col_clues = [Clue(runs) for runs in request.col_clues]
    except InvalidClueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    blank = Grid.empty(len(row_clues), len(col_clues))
    result = solve(blank, row_clues, col_clues, request.max_backtrack_depth)

    solution = None
    if result.grid is not None:
        # Convert the domain Grid (Cell.FILLED/EMPTY) into the plain
        # booleans the SolveResponse schema expects.
        solution = [[cell is Cell.FILLED for cell in row] for row in result.grid.rows]

    return SolveResponse(status=SolveOutcome[result.status.name], solution=solution)
