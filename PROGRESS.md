# Progress Tracker — Nonogram App

## Current stage: Stage 4 — Uniqueness Check
## Status: In Progress (implementation done, PR open, awaiting merge)
## Active branch: feature/stage-4-uniqueness-check
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
- [x] Stage 3 — Full Engine (PR #3, merged, CI run 28573557383 green)
  - `propagate()` (row/column wake-up queue) + `solve()` (propagation +
    backtracking, `SolveStats` for Stage 5)
  - `tests/fixtures/known_puzzles.py` populated (5x5, 10x10, 4x4 checkerboard)
  - 53 tests, 100% coverage (as of that stage)

### Current stage in progress 🚧
- [ ] Stage 4 — Uniqueness Check
  - [x] Branch `feature/stage-4-uniqueness-check` created
  - [x] `check_uniqueness(row_clues, col_clues, max_backtrack_depth=None) -> UniquenessResult`:
        solves for a first solution, then for every cell forces the opposite of
        its value (all other cells unconstrained) and re-solves; any genuine
        second solution must differ from the first at some cell, so if none of
        these per-cell searches finds an alternative, the first solution is
        provably unique. A puzzle with no solution at all reports `is_unique=False`.
  - [x] `has_unique_solution(row_clues, col_clues, max_backtrack_depth=None) -> bool`
        convenience wrapper
  - [x] `UniquenessResult` also exposes `first_solution`/`alternate_solution` for
        debugging, per the skill's suggestion
  - [x] Unit tests: known-unique (propagation-only fixture), deliberately
        ambiguous (the Stage 3 checkerboard fixture turned out to have a
        complementary second solution — reused directly), and unsolvable-puzzle
        edge case
  - [x] `ruff check .` passes; full suite green locally (59 tests, 100% coverage)
  - [ ] PR opened
  - [ ] CI green on PR
  - [ ] PR merged to `main`

### Future stages ⏳
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
- Stage 4's uniqueness check forces *every* cell to its opposite value (not just "one specific
  cell" as the skill's example phrasing suggests) before concluding a solution is unique. A
  single arbitrary cell only proves that one cell has no alternative — it can't rule out a second
  solution that differs elsewhere. Checking all cells (short-circuiting on the first alternate
  found) is the minimum needed for a mathematically sound "yes, unique" answer, so this was
  treated as a necessary refinement of the skill's example rather than a new decision to check
  with the user. Cost: O(rows × cols) `solve()` calls in the unique (worst) case — acceptable for
  now; revisit if Stage 6 generation on large grids is too slow.
- A puzzle with zero valid solutions is reported as `is_unique=False` (not an error) — "unique"
  requires exactly one solution, and zero doesn't qualify.

### Blockers / decisions needed
- (none currently open)
