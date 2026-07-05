# Progress Tracker — Nonogram App

## Current stage: MVP complete — all 9 stages done, plus a post-MVP documentation pass
## Status: Done
## Active branch: main
## Last updated: 2026-07-02

### Post-MVP: full code documentation pass
- User requested docstrings/comments throughout `src/` so the codebase is fully
  understandable on its own, beyond the project-level docs (README/PROGRESS/skill file).
- Added module-level docstrings to every file, class/dataclass-field docstrings, and
  function docstrings explaining parameters and behavior — with extra depth on the two
  most algorithmically dense spots: `solver/line_solver.py`'s forward/backward DP
  (explaining what "boundary", "mandatory gap folding", and the two-direction combine
  step actually mean) and `solver/engine.py`'s propagate/backtrack loop.
  This deliberately overrides the project's usual "no comments unless the WHY is
  non-obvious" default, since the user's explicit goal here was comprehension, not
  just maintenance.
- No logic changed — 101 tests still pass, 100% coverage maintained, `ruff check .` clean.

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
- [x] Stage 4 — Uniqueness Check (PR #4, merged, CI run 28575956258 green)
  - `check_uniqueness()` / `has_unique_solution()`: exhaustive per-cell
    opposite-value re-solve, short-circuiting on first alternate found
  - 59 tests, 100% coverage (as of that stage)
- [x] Stage 5 — Difficulty Evaluator (PR #5, merged, CI run 28579896165 green)
  - `evaluate_difficulty()`: user-confirmed formula/thresholds/reject ceiling
  - 72 tests, 100% coverage (as of that stage)
- [x] Stage 6 — Puzzle Generator (PR #6, merged, CI run 28583759903 green)
  - `PatternSource` ABC (`RandomPatternSource`, `ManualPatternSource`) +
    `generate_puzzle()` generate-and-test loop
  - 89 tests, 100% coverage (as of that stage)
- [x] Stage 7 — FastAPI Layer (PR #7, merged, CI run 28584623512 green)
  - `POST /puzzles/generate`, `POST /puzzles/solve`, `/docs`, `/openapi.json`
  - 100 tests, 100% coverage (as of that stage)
- [x] Stage 8 — Image Recognition Interface (PR #8, merged, CI run 28588885379 green)
  - `ImageToPatternConverter.convert()` stub, raises `NotImplementedError`
  - 101 tests, 100% coverage (as of that stage)
- [x] Stage 9 — Documentation & Polish (PR #9, this PR)
  - Full `README.md`: installation (incl. `pip install -e .`, verified against
    a real running `uvicorn` server, not just written from memory), running
    the API, a verified end-to-end API usage example (generate → solve),
    architecture diagram, testing instructions
  - Whole-project coverage check: 100% (target was ≥85%)
  - `PROGRESS.md` closed out — MVP ready

### Future stages ⏳
- (none — MVP complete; next phases are the separate TypeScript/React frontend
  and the image-recognition implementation behind Stage 8's stub interface,
  both explicitly out of scope for this project per
  `NONOGRAM_APP_SKILL.md` Section 0)

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
- `max_attempts` on `generate_puzzle()` has no default (required parameter), unlike
  `max_backtrack_depth`'s `None`-means-unlimited default. Unlike backtracking (a complete search
  bounded by grid size, so "unlimited" is safe), the space of random *patterns* to try is
  unbounded — an unlimited default here risks a genuine infinite loop if a requested difficulty is
  structurally unreachable at a given size. Rather than inventing a magic default number, the
  caller must decide (Stage 7's API layer can pick one informed by real performance data once it
  exists).
- `generate_puzzle()` reconciles two slightly different descriptions in the skill (the pseudocode
  raises on exhausting `max_attempts`; the prose says to "return the closest match found... with a
  clear flag"): it returns the closest-category match with `exact_match=False` if attempts are
  exhausted but *some* valid (unique, human-suitable) puzzle was found, and only raises
  `GenerationTimeoutError` if *no* valid puzzle was found at all. Treated as a natural synthesis of
  the skill's own two statements, not a new ambiguous decision needing separate sign-off.
- `PatternSource` is an ABC (`RandomPatternSource`, `ManualPatternSource` now) rather than a bare
  function, specifically so the future image-based source (explicitly flagged as a later phase in
  the skill's locked decisions) can be added as another implementation without touching
  `puzzle_generator.py` — directly serves the skill's own "no architecture change needed" goal for
  that phase.
- `GenerateResponse` deliberately excludes the solution grid. The skill describes
  `POST /puzzles/solve` as existing "for future use by the frontend to validate a user's solution
  too" — which only makes sense if `/generate` withholds the answer in the first place (otherwise
  there'd be nothing to validate against). Treated as a direct, low-risk inference from the skill's
  own stated purpose for the solve endpoint, not a new decision needing separate sign-off.
- `POST /puzzles/generate` always uses `RandomPatternSource` (with an optional `seed` for
  determinism) — there's no way to submit a `ManualPatternSource` pattern over HTTP, since manual
  patterns are a testing/internal-tooling concern, not something an API client would supply this
  way. The `ManualPatternSource` class itself remains available for direct Python use (as Stage 6's
  tests do).
- Domain exceptions (`GenerationTimeoutError`, `InvalidClueError`) are translated to HTTP 422 at
  the router boundary; unexpected/unanticipated errors are left to FastAPI's default 500 handling
  rather than being caught broadly, since masking unknown failures as generic errors would hide
  real bugs.
- `ImageToPatternConverter` (Stage 8) is a plain class, not `abc.ABC` with `@abstractmethod`. The
  skill's spec says the *method* should raise `NotImplementedError` and that a test should confirm
  that — with `abc.ABC`/`@abstractmethod`, the base class couldn't be instantiated at all (a
  `TypeError` at construction, not a `NotImplementedError` from calling `convert()`), which doesn't
  match either the letter or the spirit of the stated test. A plain class with a
  `raise NotImplementedError` body matches the skill's literal wording exactly.

### Blockers / decisions needed
- (none currently open)
