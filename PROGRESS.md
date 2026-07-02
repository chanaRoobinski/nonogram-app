# Progress Tracker — Nonogram App

## Current stage: Stage 6 — Puzzle Generator
## Status: In Progress (implementation done, PR open, awaiting merge)
## Active branch: feature/stage-6-puzzle-generator
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
- [x] Stage 4 — Uniqueness Check (PR #4, merged, CI run 28575956258 green)
  - `check_uniqueness()` / `has_unique_solution()`: exhaustive per-cell
    opposite-value re-solve, short-circuiting on first alternate found
  - 59 tests, 100% coverage (as of that stage)
- [x] Stage 5 — Difficulty Evaluator (PR #5, merged, CI run 28579896165 green)
  - `evaluate_difficulty()`: user-confirmed formula/thresholds/reject ceiling
  - 72 tests, 100% coverage (as of that stage)

### Current stage in progress 🚧
- [ ] Stage 6 — Puzzle Generator
  - [x] Branch `feature/stage-6-puzzle-generator` created
  - [x] `pattern_source.py`: `PatternSource` ABC (`generate(num_rows, num_cols)
        -> Grid`) so a future image-based source (Stage 8) can plug in without
        changing `puzzle_generator.py`. `RandomPatternSource` (noise + majority-
        rule smoothing pass) and `ManualPatternSource` (wraps a hand-built grid)
        implement it now, per the skill's "manual/random now; image-based later"
  - [x] `line_clue(cells) -> Clue` / `extract_clues(pattern) -> (row_clues,
        col_clues)` — the public version of clue-derivation; refactored
        `tests/fixtures/known_puzzles.py` and `test_solver_pipeline.py` to reuse
        it instead of keeping their own private duplicate implementations
  - [x] `puzzle_generator.py`: `generate_puzzle(num_rows, num_cols,
        requested_category, max_attempts, pattern_source=None,
        max_backtrack_depth=None) -> Puzzle` — the generate-and-test loop
        (unique solution check → solve → evaluate difficulty → reject if not
        `suitable_for_human`). Returns the closest match found if
        `max_attempts` is exhausted without an exact match
        (`Puzzle.exact_match=False`); raises `GenerationTimeoutError` only if
        no valid puzzle was found at all
  - [x] `GenerationTimeoutError` added to `core/exceptions.py`
  - [x] Unit tests for `pattern_source.py` and `puzzle_generator.py`, including
        a monkeypatched test to deterministically exercise the
        "reject an unsuitable-for-human candidate" branch (naturally-occurring
        random patterns turned out to rarely exceed the score-100 ceiling —
        smoothed/noise patterns tend to be over-constrained rather than
        ambiguous, so real search wasn't a reliable way to hit that branch)
  - [x] Integration test extending `test_generate_and_evaluate.py`: requesting
        Easy/Medium at 10x10 with a fixed seed actually returns a puzzle
        evaluated at that difficulty with a unique solution (Hard/Very Hard
        weren't reliably reachable within a reasonable attempt budget at this
        pattern-source configuration — not pursued further, see decisions below)
  - [x] `ruff check .` passes; full suite green locally (89 tests, 100% coverage)
  - [ ] PR opened
  - [ ] CI green on PR
  - [ ] PR merged to `main`

### Future stages ⏳
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

### Blockers / decisions needed
- (none currently open)
