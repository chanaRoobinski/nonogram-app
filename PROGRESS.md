# Progress Tracker — Nonogram App

## Current stage: Stage 0 — Project Scaffolding & CI
## Status: In Progress
## Active branch: main
## Last updated: 2026-07-02

### Completed stages ✅
- (none yet)

### Current stage in progress 🚧
- [ ] Stage 0 — Project Scaffolding & CI
  - [x] Folder structure created (src/nonogram/*, tests/*)
  - [x] `.venv` created with Python 3.10.7
  - [x] `requirements.txt` / `requirements-dev.txt` (pytest, pytest-cov, ruff)
  - [x] `pyproject.toml`
  - [x] `.github/workflows/ci.yml`
  - [x] Dummy smoke test passes locally (`pytest --cov=src`)
  - [x] `ruff check .` passes locally
  - [ ] GitHub repo created (`nonogram-app`, public)
  - [ ] Initial commit pushed to `main`
  - [ ] CI confirmed green on GitHub Actions

### Future stages ⏳
- [ ] Stage 1 — Core Data Structures
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
