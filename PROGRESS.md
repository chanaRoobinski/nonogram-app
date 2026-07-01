# Progress Tracker — Nonogram App

## Current stage: Stage 2 — Line Solver
## Status: Not started
## Active branch: main
## Last updated: 2026-07-02

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI (pushed directly to `main`, CI run 28551662417 green)
  - Repo: https://github.com/chanaRoobinski/nonogram-app
- [x] Stage 1 — Core Data Structures (PR #1, merged, CI run 28552133300 green)
  - `Clue`, `Cell`/`Line`, `Grid` (with `transpose()`), `exceptions.py`
  - 28 unit tests, 100% coverage on `core`

### Current stage in progress 🚧
- [ ] Stage 2 — Line Solver
  - [ ] Branch `feature/stage-2-line-solver` created
  - [ ] `solve_line(clue: Clue, current_state: Line) -> Line` implemented (DP-based)
  - [ ] Edge cases: empty clue, fully-known line, contradiction, partial-overlap-only case
  - [ ] Unit tests covering all edge cases
  - [ ] PR opened and merged

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
