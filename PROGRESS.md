# Progress Tracker — Nonogram App

## Current stage: Stage 2 — Line Solver
## Status: In Progress (implementation done, PR open, awaiting merge)
## Active branch: feature/stage-2-line-solver
## Last updated: 2026-07-02

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI (pushed directly to `main`, CI run 28551662417 green)
  - Repo: https://github.com/chanaRoobinski/nonogram-app
- [x] Stage 1 — Core Data Structures (PR #1, merged, CI run 28552133300 green)
  - `Clue`, `Cell`/`Line`, `Grid` (with `transpose()`), `exceptions.py`
  - 28 unit tests, 100% coverage on `core`

### Current stage in progress 🚧
- [ ] Stage 2 — Line Solver
  - [x] Branch `feature/stage-2-line-solver` created
  - [x] `solve_line(clue, current_state) -> Line` implemented: DP with
        mandatory-gap-folded run placement (forward pass) + suffix-feasibility pass
        (backward), combined to mark each cell FILLED-achievable / EMPTY-achievable
        across all valid arrangements
  - [x] Raises `ContradictionError` when no arrangement is consistent with known cells
  - [x] 13 unit tests (incl. partial-overlap-only, contradiction, empty clue,
        mandatory gap enforcement, already-known-line pass-through), 100% coverage
        on `solver`
  - [x] `ruff check .` passes; full suite green locally (41 tests, 100% coverage)
  - [ ] PR opened
  - [ ] CI green on PR
  - [ ] PR merged to `main`

### Future stages ⏳
- [ ] Stage 3 — Full Engine (propagation + backtracking)
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

### Blockers / decisions needed
- (none currently open)
