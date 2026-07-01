# Skill: Building a Nonogram Puzzle Generator App (Difficulty-Aware)

## ⚠️ Read this first — no prior context assumed

If you are an AI agent or developer picking this file up **cold, with no memory of any previous
conversation**, this section gives you everything you need. Do not assume you know anything about
this project beyond what is written here and in `PROGRESS.md`.

**What this project is:** A tool that programmatically generates nonogram puzzles (also known as
Picross, Griddlers, or Hanjie) at a difficulty level chosen by the user, and can also solve them.

**What a nonogram is:** A logic puzzle on a grid. Each row and column has a list of numbers (a
"clue") describing the lengths of consecutive filled-cell runs in that row/column, in order, with
at least one empty cell between runs. Solving means filling the grid so all row and column clues
are simultaneously satisfied, which reveals a hidden picture.

**What "always" applies in this document:** Every rule, convention, and decision below is binding
unless the user (the project owner) explicitly says otherwise in the current conversation. If you
are unsure whether something changed, **ask the user** — do not guess, and do not silently deviate
from this document.

**Your first action in any session:** Read `PROGRESS.md` in the project root (once it exists —
see Stage 0) before doing anything else. It is the single source of truth for what has been done
and what comes next. This skill file (`NONOGRAM_APP_SKILL.md`) describes *how* to work; `PROGRESS.md`
describes *where things currently stand*.

---

## 0. Locked technology decisions (do not change without explicit user approval)

| Decision | Value |
|---|---|
| Language | Python 3.10+ (updated 2026-07-01: 3.12 not available in dev environment, only 3.10.7 was installed; user approved using 3.10 instead) |
| Package/venv management | plain `pip` + `venv` |
| Web framework (backend) | FastAPI |
| Frontend | **Not part of this phase.** A separate TypeScript/React frontend will be built later, as an entirely separate project/codebase. Do not build any frontend code as part of this skill. |
| Testing | `pytest` |
| CI | GitHub Actions — runs automatically on every push and pull request |
| Repository | GitHub, public, repo name `nonogram-app` |
| License | MIT |
| GitHub auth | Uses the GitHub CLI (`gh`). If `gh auth status` fails or shows an expired token, run `gh auth login` before doing anything else that touches GitHub. |

> **Future scope, explicitly out of scope for now:** An advanced image-recognition module that
> converts an uploaded image into a nonogram pattern (image-to-nonogram) is planned for a **future
> phase**, not part of this MVP. The project structure includes a placeholder/interface for it
> (see Stage 8) so no architecture change will be needed when that phase begins.

**Rationale note (for context, not something to re-litigate):** Python was chosen specifically
because the future image-recognition phase will need Python's image-processing ecosystem (e.g.
OpenCV/PIL), and it's preferable to keep the whole backend in one language rather than splitting
solver logic and image logic across two stacks.

**All prior open questions have been answered — nothing is pending here.** If you notice anything
in this document phrased as an unresolved question, treat that as a bug in the document and ask
the user before proceeding.

---

## 1. Binding working principles

1. **Every stage = its own branch + its own PR.** Never work directly on `main`, except for the
   one-time exception described in Stage 0 step 10 (initial scaffolding push).
2. **Never move to the next stage until the current one is fully green**: all tests pass, CI is
   green, and the PR for that stage has been merged into `main`.
3. **Every module gets both unit tests (in isolation) and integration tests (combined with
   previously-built modules)** before its stage is considered closed.
4. **`PROGRESS.md` is updated at the end of every stage**, and ideally at meaningful checkpoints
   within a stage too. It is the only source of truth for project state — more authoritative than
   this file for "where are we now," though this file remains authoritative for "how do we work."
5. **Commit messages** follow Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`,
   `refactor:`.
6. **No skipping stages.** Even if it's tempting to jump ahead to the generator before the solver
   is stable, don't — the dependency chain in Section 16 explains why each stage needs the ones
   before it.
7. **No guessing on significant decisions.** If you hit a design decision not covered by this
   document (data representation choices, timeout values, scoring weights, etc.), stop, record it
   under "Blockers / decisions needed" in `PROGRESS.md`, and ask the user. Do not proceed on an
   assumption.

---

## 2. Project structure (created in Stage 0)

```
nonogram-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── nonogram/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── grid.py          # data structures: Grid, Clue, Line
│       │   └── exceptions.py
│       ├── solver/
│       │   ├── __init__.py
│       │   ├── line_solver.py   # constraint propagation for a single line
│       │   ├── engine.py        # full propagation loop + backtracking
│       │   └── uniqueness.py    # unique-solution check
│       ├── difficulty/
│       │   ├── __init__.py
│       │   └── evaluator.py     # difficulty scoring based on solve statistics
│       ├── generator/
│       │   ├── __init__.py
│       │   ├── pattern_source.py    # pattern sources (manual/random now; image-based later)
│       │   └── puzzle_generator.py  # generate-and-test loop targeting a requested difficulty
│       ├── image_recognition/    # *** STUB ONLY at this phase ***
│       │   ├── __init__.py
│       │   └── interface.py      # future interface definition, no implementation
│       └── api/
│           ├── __init__.py
│           ├── main.py           # FastAPI app
│           ├── routers/
│           │   ├── solver_router.py
│           │   └── generator_router.py
│           └── schemas.py        # Pydantic models
├── tests/
│   ├── unit/
│   │   ├── test_grid.py
│   │   ├── test_line_solver.py
│   │   ├── test_engine.py
│   │   ├── test_uniqueness.py
│   │   ├── test_evaluator.py
│   │   └── test_puzzle_generator.py
│   ├── integration/
│   │   ├── test_solver_pipeline.py
│   │   ├── test_generate_and_evaluate.py
│   │   └── test_api.py
│   └── fixtures/
│       └── known_puzzles.py      # known puzzles with known solutions, for regression tests
├── PROGRESS.md                    # *** state file — always read/update this ***
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml                 # (or setup.cfg — decide in Stage 0)
├── .gitignore
├── README.md
└── LICENSE
```

---

## 3. `PROGRESS.md` — the continuity protocol

This is the single most important file for resuming work across sessions, days, or different
agents. **At the start of any work session, read this file before anything else in the project.**

Template for the file's contents:

```markdown
# Progress Tracker — Nonogram App

## Current stage: Stage 2 — Line Solver
## Status: In Progress
## Active branch: feature/stage-2-line-solver
## Last updated: 2026-07-01

### Completed stages ✅
- [x] Stage 0 — Project Scaffolding & CI          (PR #1, merged)
- [x] Stage 1 — Core Data Structures               (PR #2, merged)

### Current stage in progress 🚧
- [ ] Stage 2 — Line Solver
  - [x] Implement `line_solver.py` (dynamic programming for overlap detection)
  - [x] Basic unit tests
  - [ ] Edge-case tests (full/empty row, clue of [0])
  - [ ] Self code review + run CI
  - [ ] Open PR

### Future stages ⏳
- [ ] Stage 3 — Full Engine (propagation + backtracking)
- [ ] Stage 4 — Uniqueness Check
- [ ] Stage 5 — Difficulty Evaluator
- [ ] Stage 6 — Puzzle Generator
- [ ] Stage 7 — FastAPI Layer
- [ ] Stage 8 — Image Recognition Interface (stub only)
- [ ] Stage 9 — Documentation & Polish

### Decisions made along the way
- (example: "Decided that a clue of 0 is represented as an empty list [] rather than [0]")

### Blockers / decisions needed
- (if a genuinely open question stopped work, record it here — do not guess an answer)
```

**Iron rule:** if you hit a significant decision not defined in this skill document (e.g., exactly
how to represent an empty clue, what the backtracking timeout should be) — **stop, ask the user,
and record the answer here.** Do not guess.

---

## 4. Stage 0 — Project setup

### Goal
A complete working skeleton: a GitHub repo, the folder structure, a virtual environment, and a
CI pipeline that runs successfully — even before any real logic exists.

### Steps
1. **Re-authenticate the GitHub CLI**: run `gh auth login` (the existing token is expired). Confirm
   with `gh auth status` that authentication is valid before continuing.
2. Create the `nonogram-app` repository on GitHub (public):
   `gh repo create nonogram-app --public --source=. --remote=origin`.
3. `git init` (if not already created automatically by `gh repo create`), create `.gitignore`
   (Python template), an initial `README.md`, and `LICENSE` (MIT).
4. Create a virtual environment: `python -m venv .venv`, then activate it.
5. Create `requirements.txt` (empty for now) and `requirements-dev.txt` (pytest, pytest-cov,
   ruff or black — pick one for linting/formatting).
6. Create the full folder structure from Section 2 (with empty `__init__.py` files and placeholder
   files where needed).
7. Write `.github/workflows/ci.yml`:
   - Triggers: `push` and `pull_request` on `main`.
   - Job: set up Python 3.10 — `pip install -r requirements-dev.txt` — `pytest --cov=src` —
     (optional) `ruff check`.
8. Write the initial `PROGRESS.md` (template from Section 3).
9. First commit: `chore: initial project scaffolding`.
10. Push directly to `main` (this is the **only** stage where working directly on `main` is
    allowed — before any real logic exists).

### Tests for this stage
- CI **runs successfully** even without real tests yet (e.g., one "dummy" test that always
  passes, just to confirm the pipeline itself is wired correctly).
- `pip install -r requirements-dev.txt` succeeds from a clean clone.

### Definition of Done
- [ ] Repo exists on GitHub, public, with a README
- [ ] CI is green
- [ ] `PROGRESS.md` updated to "Stage 0 complete, Stage 1 next"

---

## 5. Stage 1 — Core data structures (`core/`)

### Goal
Define the project's foundational vocabulary before any logic is built on top of it.

### What to build
- `Clue`: a list of non-negative integers (e.g. `[3, 1]`), with validation (no negative numbers,
  etc.).
- `Line`: a row/column representation — an array of cells, each cell being `FILLED` / `EMPTY` /
  `UNKNOWN` (recommend an `Enum`, not `bool`, since the "unknown" state is essential).
- `Grid`: a matrix of `Line`s, accessible both by row and by column (via transposition).
- Dedicated exceptions in `exceptions.py`: `InvalidClueError`, `ContradictionError`, etc. (used by
  the solver later).

### Tests
- **Unit**: valid/invalid `Clue` creation, `Grid` sizing, correct transposition (row 3 of a grid
  equals column 3 of its transpose), grid equality checks.
- **No integration tests yet** — there are no other modules to combine with.

### Git
- Branch: `feature/stage-1-core-data-structures`
- PR with a short description + a link to the relevant entry in `PROGRESS.md`
- Merge only after CI is green

### Definition of Done
- [ ] Test coverage ≥90% for the `core` module
- [ ] PR merged
- [ ] `PROGRESS.md` updated

---

## 6. Stage 2 — Line solver (single-line constraint solving)

### Goal
Implement the DP algorithm discussed earlier: given a `Clue` and the current state of a line
(including any already-known cells), return which cells are certainly `FILLED`, which are
certainly `EMPTY`, given all valid arrangements consistent with the clue.

### What to build
- `line_solver.py`: a core function `solve_line(clue: Clue, current_state: Line) -> Line` (returns
  an updated line — not necessarily fully solved, only what's certain).
- A DP-based implementation (a table tracking "can the first part of the clue be matched against
  this prefix of the line, given known cells").
- Edge cases: an empty clue (`[]`), an already-fully-known line, and contradictions (raise
  `ContradictionError`).

### Tests
- **Unit**: dozens of cases including basic overlap, a line with some cells already known, a clue
  that cannot fit the line (contradiction), clues of `[0]`/`[]`.
- Required: at least one case with **partial overlap only** (i.e. the function doesn't solve
  everything at once, only what's certain).

### Git
- Branch: `feature/stage-2-line-solver`

### Definition of Done
- [ ] All edge cases covered by tests
- [ ] PR merged, `PROGRESS.md` updated

---

## 7. Stage 3 — Full engine (constraint propagation + backtracking)

### Goal
Assemble `line_solver` into a full-grid solver, including cross-referencing between rows and
columns, with a backtracking fallback when propagation alone gets stuck.

### What to build
- `engine.py`:
  - `propagate(grid) -> Grid`: a loop that runs `solve_line` on rows/columns alternately until no
    further change occurs (only re-running lines that were "woken up" by a change in the
    perpendicular direction).
  - `solve(grid, max_backtrack_depth=None) -> SolveResult`: calls `propagate`; if it gets stuck,
    picks an unknown cell, guesses a value, and continues recursively; on contradiction, it
    backtracks.
  - **Important**: the engine must track and return **how many times each stage ran** (pure
    propagation steps? backtracking depth reached?) — this feeds `difficulty/evaluator.py` later.
    Designing this interface now avoids a refactor in Stage 5.
- A timeout/max-iteration cap to prevent infinite runs on large grids.

### Tests
- **Unit**: small known puzzles (5×5, 10×10) with expected solutions — including some solvable by
  propagation alone and some that require backtracking.
- **Integration**: `tests/integration/test_solver_pipeline.py` — takes a full puzzle (grid +
  clues), runs `solve`, and compares against a known solution from `fixtures/known_puzzles.py`.
- Performance test: measure run time on a 20×20 grid (not a hard assertion on time, but documents
  a baseline).

### Git
- Branch: `feature/stage-3-solver-engine`

### Definition of Done
- [ ] All puzzles in `known_puzzles.py` solve correctly
- [ ] A mechanism exists for recording solve statistics (needed by the next stage)

---

## 8. Stage 4 — Unique-solution check (`uniqueness.py`)

### Goal
Confirm a puzzle has exactly one valid solution — critical before generating puzzles for
distribution.

### What to build
- `has_unique_solution(clues) -> bool` (or also returns the second solution if one exists, for
  debugging).
- Method: find a first solution with `engine.solve`, then search for a second solution under a
  constraint of "different from the first solution" (e.g. by forcing one specific cell to the
  opposite value and checking whether a solution still exists).

### Tests
- **Unit**: a puzzle with a known unique solution — `True`. A deliberately ambiguous puzzle
  (clues consistent with multiple solutions) — `False`.

### Git
- Branch: `feature/stage-4-uniqueness-check`

---

## 9. Stage 5 — Difficulty evaluator (`difficulty/evaluator.py`)

### Goal
Convert the solve statistics from Stage 3 (amount of propagation, backtracking depth reached,
number of initial "entry points") into a score/category.

### What to build
- `evaluate_difficulty(solve_stats) -> DifficultyResult` (a numeric score + a category:
  Easy / Medium / Hard / Very Hard).
- A scoring formula along the lines discussed earlier (basic overlap = low weight, nested
  backtracking = high weight).
- **Note:** if the exact weights aren't settled, that is a design decision that needs the user's
  sign-off before implementation (how exactly "backtracking depth 2" maps to a difficulty score).
  **If you reach this point without a decision, record it as an open question in `PROGRESS.md`
  and ask the user.**

### Tests
- **Unit**: synthetic inputs (mocked statistics) — expected difficulty category.
- **Integration**: `test_generate_and_evaluate.py` — takes real puzzles from Stages 3–4, runs the
  evaluator, and checks the result is sensible (a puzzle that required nested backtracking must
  not come out as "Easy").

---

## 10. Stage 6 — Difficulty-targeted puzzle generator (`generator/`)

### Goal
The module the end user actually wants: "give me a puzzle of difficulty X at size Y."

### What to build
- `pattern_source.py`: an initial pattern source — **controlled randomness** (not image-based
  yet!). For example, an algorithm that generates patterns that aren't "too noisy" (a simple
  cellular automaton, or noise plus smoothing).
- `puzzle_generator.py`: the generate-and-test loop:
  ```
  while attempts < max_attempts:
      pattern = pattern_source.generate(size)
      clues = extract_clues(pattern)
      if not uniqueness.has_unique_solution(clues): continue
      stats = engine.solve(clues, collect_stats=True)
      difficulty = evaluator.evaluate_difficulty(stats)
      if difficulty.category == requested_category:
          return Puzzle(pattern, clues, difficulty)
  raise GenerationTimeoutError
  ```
- A `max_attempts` cap with sensible failure handling (e.g., return the closest match found, with
  a clear flag indicating it didn't hit the exact requested difficulty).

### Tests
- **Unit**: pattern sources return valid grids at the requested sizes.
- **Integration**: requesting an "Easy" 10×10 puzzle actually returns a puzzle evaluated as Easy,
  with a unique solution. Same for other difficulty levels (with a high enough `max_attempts` in
  the test, and a fixed random seed so the test is deterministic!).

---

## 11. Stage 7 — API layer (FastAPI)

### Goal
Expose the capabilities as a REST API, ready for a future frontend to connect to.

### What to build
- `api/schemas.py`: Pydantic models (`PuzzleRequest`, `PuzzleResponse`, `SolveRequest`, etc.).
- `api/routers/generator_router.py`: `POST /puzzles/generate` (size + difficulty → puzzle).
- `api/routers/solver_router.py`: `POST /puzzles/solve` (clues → solution — for future use by the
  frontend to validate a user's solution too).
- `api/main.py`: assembles the app, including FastAPI's automatic docs (`/docs`).

### Tests
- **Integration**: `test_api.py` using FastAPI's `TestClient` — real calls to the endpoints,
  checking status codes and response schemas.

---

## 12. Stage 8 — Image-recognition interface (stub only, no implementation)

### Goal
Prepare a clear "slot" for the future without actually implementing it now (this is an explicitly
future phase).

### What to build
- `image_recognition/interface.py`: an `abstract class ImageToPatternConverter` with a method
  `convert(image_path) -> Grid`, **with no implementation** (`raise NotImplementedError`).
- A clear docstring stating this is a placeholder for a future phase, including the candidate
  libraries already discussed (OpenCV / PIL).

### Tests
- One test: confirm the interface exists and raises `NotImplementedError` as expected (this
  prevents an accidental partial implementation from being forgotten/left incomplete).

---

## 13. Stage 9 — Documentation and polish

- Full `README.md`: installation, running the app, an API usage example.
- Brief architecture documentation (a textual diagram of modules and their dependencies).
- Overall test coverage check (`pytest --cov` across the whole project, target: ≥85%).
- Close out `PROGRESS.md` with "all stages complete, MVP ready."

---

## 14. PR template (use for every stage)

```markdown
## Stage: [stage number and name]

### What was done
- ...

### How it was verified
- [ ] Local pytest passes
- [ ] CI is green
- [ ] Test coverage checked

### Related PROGRESS.md update
Updates status to: [...]
```

---

## 15. Protocol for resuming work after a break (critical)

Every time you start a new work session on this project:

1. `git status` + `git branch` — confirm where you are.
2. Read `PROGRESS.md` — what's the current stage, what's already done within it.
3. Run `pytest` locally — confirm the saved state is actually "green."
4. Check whether the current branch already has an open PR (`gh pr status`).
5. Continue **exactly from the open checklist item** in the current stage in `PROGRESS.md` — do
   not start a new stage before the current one is closed.
6. If there are "Blockers / decisions needed" recorded in `PROGRESS.md`, ask the user before
   proceeding.

---

## 16. Dependencies between stages (why this order, and not another)

```
Stage 0 (scaffolding)
   ↓
Stage 1 (core data) ─── everything depends on this
   ↓
Stage 2 (line solver) ─── the smallest algorithmic core, testable in isolation
   ↓
Stage 3 (full engine) ─── depends on line solver; produces statistics for Stage 5
   ↓
Stage 4 (uniqueness) ─── depends on the engine
   ↓
Stage 5 (difficulty evaluator) ─── depends on statistics from the engine
   ↓
Stage 6 (generator) ─── depends on all previous stages (uniqueness + evaluator + engine)
   ↓
Stage 7 (API) ─── wraps the generator + solver
   ↓
Stage 8 (image stub) ─── independent in principle, but placed last so it doesn't distract from the logical MVP
   ↓
Stage 9 (docs/polish)
```

**You cannot skip to Stage 6 without Stages 3+4+5 done** — "generate-and-test targeting a
difficulty level" is meaningless without a reliable difficulty evaluator.

---

*This document is a living document. If a significant decision is made during actual work that
contradicts or extends it, update this document itself — not just `PROGRESS.md`.*
