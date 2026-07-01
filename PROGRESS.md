# Progress Tracker — Nonogram App

## Current stage: Stage 1 — Core Data Structures
## Status: Not started
## Active branch: main
## Last updated: 2026-07-02

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI (pushed directly to `main`, CI run 28551662417 green)
  - Repo: https://github.com/chanaRoobinski/nonogram-app

### Current stage in progress 🚧
- [ ] Stage 1 — Core Data Structures
  - [ ] Branch `feature/stage-1-core-data-structures` created
  - [ ] `Clue` implemented + validated
  - [ ] `Line` implemented (FILLED/EMPTY/UNKNOWN enum)
  - [ ] `Grid` implemented (row/column access via transposition)
  - [ ] `exceptions.py`: `InvalidClueError`, `ContradictionError`
  - [ ] Unit tests, ≥90% coverage on `core`
  - [ ] PR opened and merged

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

### Blockers / decisions needed
- (none currently open)
