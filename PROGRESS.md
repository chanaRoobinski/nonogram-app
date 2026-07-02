# Progress Tracker — Nonogram App

## Current stage: Stage 3 — Full Engine (propagation + backtracking)
## Status: In Progress (implementation done, PR open, awaiting merge)
## Active branch: feature/stage-3-solver-engine
## Last updated: 2026-07-02

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI (pushed directly to `main`, CI run 28551662417 green)
  - Repo: https://github.com/chanaRoobinski/nonogram-app
- [x] Stage 1 — Core Data Structures (PR #1, merged, CI run 28552133300 green)
  - `Clue`, `Cell`/`Line`, `Grid` (with `transpose()`), `exceptions.py`
  - 28 unit tests, 100% coverage on `core`
- [x] Stage 2 — Line Solver (PR #2, merged, CI run 28552534960 green)
  - `solve_line(clue, current_state) -> Line`: DP with mandatory-gap-folded run
    placement + forward/backward feasibility passes
  - 13 unit tests, 100% coverage on `solver` (as of that stage)

### Current stage in progress 🚧
- [ ] Stage 3 — Full Engine (propagation + backtracking)
  - [x] Branch `feature/stage-3-solver-engine` created
  - [x] `propagate(grid, row_clues, col_clues, dirty_rows=None, dirty_cols=None) -> (Grid, PropagationStats)`:
        row/column wake-up queue — only re-checks lines woken by a change in the
        perpendicular direction; `dirty_rows`/`dirty_cols` let callers scope an
        initial re-check (used by backtracking to avoid re-solving the whole grid
        per guess)
  - [x] `solve(grid, row_clues, col_clues, max_backtrack_depth=None) -> SolveResult`:
        propagates, then guesses the first UNKNOWN cell (FILLED then EMPTY) and
        recurses on contradiction; `SolveResult.status` is one of `SOLVED`,
        `CONTRADICTION`, `MAX_DEPTH_EXCEEDED`
  - [x] `SolveStats` tracks `propagation_calls`, `lines_solved`,
        `cells_deduced_by_propagation`, `guesses`, `max_backtrack_depth` — feeds
        Stage 5's difficulty evaluator
  - [x] `tests/fixtures/known_puzzles.py` populated: a 5x5 and 10x10 puzzle solvable
        by propagation alone, plus a 4x4 checkerboard that requires backtracking
        (clues are derived automatically from each hand-authored solution, so they
        can't drift out of sync)
  - [x] Unit tests (`test_engine.py`) + integration test (`test_solver_pipeline.py`)
        against `known_puzzles.py`, plus a 20x20 performance baseline (~0.25s,
        generous 30s ceiling — informational, not a strict contract)
  - [x] `ruff check .` passes; full suite green locally (53 tests, 100% coverage)
  - [ ] PR opened
  - [ ] CI green on PR
  - [ ] PR merged to `main`

### Future stages ⏳
- [ ] Stage 4 — Uniqueness Check
- [ ] Stage 5 — Difficulty Evaluator
- [ ] Stage 6 — Puzzle Generator
- [ ] Stage 7 — FastAPI Layer
- [ ] Stage 8 — Image Recognition Interface (stub only)
- [ ] Stage 9 — Documentation & Polish

### Decisions made along the way
- Python version changed from the originally-planned 3.12+ to **3.10+**: only Python 3.10.7 and
  3.9 were available in the dev environment (no 3.12). User approved using 3.10 instead
  (2026-07-02). `NONOGRAM_APP_SKILL.md` Section 0 and the CI workflow were updated to match.
- GitHub CLI (`gh`) was not pre-installed; installed via `winget install --id GitHub.cli`.
- `gh auth login --with-token` requires piping the token through a plain file (not a PowerShell
  string pipe) to avoid the token being mangled, and requires a classic PAT with `repo`,
  `read:org`, and `gist` scopes at minimum — a token missing `read:org` fails with
  "missing required scope" even though the token itself is valid.
- Empty-line `Clue` representation: `Clue([])` for a fully empty line, not `Clue([0])`. Every
  value inside a non-empty clue must be a positive integer (>= 1); a `0` embedded in the list
  (e.g. `[0, 3]`) is invalid and raises `InvalidClueError`. User confirmed 2026-07-02.
- `Grid` stores only cell state (rows of `Cell` values); `Clue`s are a separate concern, matched
  against rows/columns by index later by the solver — not stored inside `Grid` itself.
- Stage 3 deviates from the skill's literal `propagate(grid) -> Grid` / `solve(grid, ...) -> SolveResult`
  signatures by also taking `row_clues`/`col_clues` as explicit parameters, and `propagate()`
  returns `(Grid, PropagationStats)` rather than just `Grid`. This follows directly from the
  Stage 1 decision that `Grid` doesn't store clues, plus Stage 3's own requirement to track solve
  statistics — not treated as a new ambiguous decision needing sign-off, just documented here.
- `max_backtrack_depth` (and no separate hardcoded iteration/timeout cap) defaults to `None`
  (unlimited), matching the literal default in the skill's own `solve()` signature. Rather than
  inventing an arbitrary default timeout number, the cap is left fully caller-configurable;
  Stage 6's generator can pass a bounded value when it needs one.

### Blockers / decisions needed
- (none currently open)
