# Setup and run

## Requirements

| Requirement | Notes |
|-------------|--------|
| **Python** | **3.14 or newer** (`requires-python` in `pyproject.toml`) |
| **OS** | Developed on Linux; terminal should support Textual (modern `$TERM`). |
| **Network** | Only needed for `pip install` during bootstrap, not for gameplay. |

Do **not** install the project into the **system** Python for day-to-day work. Use a **project virtual environment** (`.venv`).

## First-time setup (virtual environment)

From the repository root:

```bash
bash scripts/bootstrap.sh
```

This script:

1. Creates **`.venv`** next to the project (if it does not exist).
2. Activates it and upgrades **pip**.
3. Installs the package in **editable** mode with **dev** dependencies:  
   `pip install -e ".[dev]"`  
   (runtime deps: Textual, argon2-cffi; dev: pytest, pytest-cov, pytest-asyncio).
4. Runs **`python -m galactic_wrestling.ai_opponents`** to seed the **AI opponent** roster when archetypes are missing (safe to run repeatedly).

You can re-run the seed module anytime:

```bash
python -m galactic_wrestling.ai_opponents
```

Activate the venv in each new shell:

```bash
source .venv/bin/activate
```

(On Windows, use `.venv\Scripts\activate`.)

## Running tests

```bash
bash scripts/run-tests.sh
```

Requires `.venv` to exist (run `bootstrap.sh` first).

## Running the game

With the venv activated:

```bash
python -m galactic_wrestling
```

or:

```bash
galactic-wrestling
```

## Data directory

By default, saves and accounts go under:

`~/.galactic-wrestling/`

AI opponent wrestlers are stored under `ai_opponents/` inside that directory (see [Game overview](game.md)).

Override for tests or portable installs:

```bash
export GALACTIC_WRESTLING_DATA_DIR=/path/to/data
```

## Troubleshooting

- **`No module named galactic_wrestling`** — Activate `.venv` or run `pip install -e ".[dev]"` inside the venv.
- **Tests fail on coverage** — Run `bash scripts/run-tests.sh` and read missing lines in the report; add tests or adjust omit list with documentation (see [Testing and coverage](testing-and-coverage.md)).
