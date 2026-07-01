# Progress Tracker — Nonogram App

## Current stage: Stage 1 — Core Data Structures
## Status: In Progress (implementation done, PR pending)
## Active branch: feature/stage-1-core-data-structures
## Last updated: 2026-07-02

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI (pushed directly to `main`, CI run 28551662417 green)
  - Repo: https://github.com/chanaRoobinski/nonogram-app

### Current stage in progress 🚧
- [ ] Stage 1 — Core Data Structures
  - [x] Branch `feature/stage-1-core-data-structures` created
  - [x] `Clue` implemented + validated (non-bool ints, each run >= 1)
  - [x] `Line` implemented (FILLED/EMPTY/UNKNOWN enum-backed cells)
  - [x] `Grid` implemented (row/column access via transposition)
  - [x] `exceptions.py`: `InvalidClueError`, `ContradictionError` (+ `NonogramError` base)
  - [x] Unit tests: 28 tests, 100% coverage on `core` (target was ≥90%)
  - [x] `ruff check .` passes; full suite green locally
  - [ ] PR opened
  - [ ] CI green on PR
  - [ ] PR merged to `main`

### Future stages ⏳
- [ ] Stage 2 — Line Solver
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
