# nonogram-app

A tool that programmatically generates nonogram puzzles (Picross / Griddlers / Hanjie) at a
difficulty level chosen by the user, and can also solve them.

Project status and stage-by-stage progress are tracked in [PROGRESS.md](PROGRESS.md). The full
build plan and working conventions are documented in
[NONOGRAM_APP_SKILL.md](NONOGRAM_APP_SKILL.md).

## Status

This project is under active, staged development. See `PROGRESS.md` for the current stage.

## Development setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
pytest
```
