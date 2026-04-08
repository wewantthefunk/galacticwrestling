# Galactic Wrestling

Terminal deckbuilder wrestling game (ASCII). Work in progress.

**Full documentation:** see the [docs/](docs/README.md) folder (game vision, architecture, testing standards, setup, and feature plans).

## Requirements

- Python 3.14+

## Development workflow

Use a project-local virtual environment (do not install into the system interpreter):

```bash
bash scripts/bootstrap.sh
source .venv/bin/activate
```

Run the automated test suite (with coverage) before manual testing:

```bash
bash scripts/run-tests.sh
```

`run-tests.sh` expects `.venv` to exist; it runs `pytest` with the settings in `pyproject.toml` (100% line and branch coverage on measured modules).

### Run the game

With the venv activated:

```bash
python -m galactic_wrestling
```

or:

```bash
galactic-wrestling
```

### Data directory

`~/.galactic-wrestling/` (override with `GALACTIC_WRESTLING_DATA_DIR`). AI opponents live in `ai_opponents/` under that root.

### AI opponents (single-player)

Bootstrap and app startup run `ensure_ai_opponents()` so six AI wrestlers exist (one per archetype). Manual re-seed: `python -m galactic_wrestling.ai_opponents`. Details: [docs/game.md](docs/game.md), [docs/plans/02-ai-opponents-single-player.md](docs/plans/02-ai-opponents-single-player.md).

### Coverage scope

Logic under `src/galactic_wrestling/` is covered by unit tests, except `ui/screens.py`, which is Textual wiring and is exercised by a small async smoke test plus manual play. Raise coverage there later with expanded Textual pilot tests if you want the metric to include the UI layer.
