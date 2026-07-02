# nonogram-app

A tool that programmatically generates nonogram puzzles (Picross / Griddlers / Hanjie) at a
difficulty level chosen by the user, and can also solve them. Exposed as a REST API (FastAPI),
ready for a frontend to connect to.

**What a nonogram is:** a logic puzzle on a grid. Each row and column has a list of numbers (a
"clue") describing the lengths of consecutive filled-cell runs in that row/column, in order, with
at least one empty cell between runs. Solving means filling the grid so all row and column clues
are simultaneously satisfied, which reveals a hidden picture.

## Status

MVP complete — all 9 stages of the build plan are done. See [PROGRESS.md](PROGRESS.md) for the
full stage-by-stage history and every non-obvious decision made along the way, and
[NONOGRAM_APP_SKILL.md](NONOGRAM_APP_SKILL.md) for the build plan and working conventions this
project followed.

**Out of scope for this phase:** a TypeScript/React frontend (a separate future project) and
image-to-nonogram conversion (stubbed in `image_recognition/interface.py` for a future phase).

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/chanaRoobinski/nonogram-app.git
cd nonogram-app
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux
pip install -r requirements-dev.txt
pip install -e .
```

## Running the API

```bash
uvicorn nonogram.api.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`, with interactive docs at
`http://127.0.0.1:8000/docs` (Swagger UI) and `http://127.0.0.1:8000/redoc`.

### API usage example

Generate a 5x5 Easy puzzle:

```bash
curl -X POST http://127.0.0.1:8000/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{"num_rows": 5, "num_cols": 5, "difficulty": "EASY", "max_attempts": 20, "seed": 42}'
```

```json
{
  "row_clues": [[4], [4], [4], [3], [1]],
  "col_clues": [[], [3], [4], [5], [4]],
  "difficulty": {"score": 0, "category": "EASY", "suitable_for_human": true},
  "exact_match": true
}
```

Note the response deliberately excludes the solution grid — a player is expected to solve the
puzzle from the clues. Validate a candidate solution (or just fetch the answer) by solving the
same clues directly:

```bash
curl -X POST http://127.0.0.1:8000/puzzles/solve \
  -H "Content-Type: application/json" \
  -d '{"row_clues": [[4], [4], [4], [3], [1]], "col_clues": [[], [3], [4], [5], [4]]}'
```

```json
{
  "status": "SOLVED",
  "solution": [
    [false, true, true, true, true],
    [false, true, true, true, true],
    [false, true, true, true, true],
    [false, false, true, true, true],
    [false, false, false, true, false]
  ]
}
```

`status` is one of `SOLVED`, `CONTRADICTION` (the clues admit no valid arrangement), or
`MAX_DEPTH_EXCEEDED` (only relevant if `max_backtrack_depth` is set in the request).

## Architecture

```
core/         Clue, Cell/Line, Grid — foundational data structures, no dependencies
   ↓
solver/       line_solver.solve_line()      — single-line constraint solving (DP)
              engine.propagate() / solve()  — full-grid propagation + backtracking
              uniqueness.has_unique_solution() — exactly-one-solution check
   ↓
difficulty/   evaluator.evaluate_difficulty() — SolveStats -> score/category
   ↓
generator/    pattern_source.PatternSource   — pluggable pattern sources
                (RandomPatternSource, ManualPatternSource; image-based later)
              puzzle_generator.generate_puzzle() — generate-and-test loop
   ↓
api/          FastAPI app, Pydantic schemas, routers — wraps generator + solver

image_recognition/   stub interface for a future phase (not wired into generator/ yet)
```

Each layer only depends on the ones above it in this diagram; `core` has no internal
dependencies, and `api` is the only layer that talks to `difficulty`/`generator`/`solver`
together.

## Testing

```bash
pytest --cov=src --cov-report=term-missing
ruff check .
```

Current coverage: 100% across all of `src` (101 tests). CI (`.github/workflows/ci.yml`) runs both
on every push and pull request against `main`.

## License

MIT — see [LICENSE](LICENSE).
