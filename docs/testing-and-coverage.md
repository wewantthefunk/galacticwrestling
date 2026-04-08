# Testing and coverage standards

## Goals

1. **Regression safety** — Refactors and new features should not break accounts, saves, or deck math without failing CI locally (`bash scripts/run-tests.sh`).
2. **Fast feedback** — Unit tests stay quick; no mandatory manual step for logic changes.
3. **Honest scope** — Coverage metrics match what we **require** vs what we **smoke-test**.

## Tooling

| Tool | Role |
|------|------|
| **pytest** | Test runner |
| **pytest-cov** | Coverage with branch coverage |
| **pytest-asyncio** | Async tests (e.g. Textual `run_test`) |

Configuration lives in **`pyproject.toml`** under `[tool.pytest.ini_options]` and `[tool.coverage.*]`.

## Running tests

```bash
bash scripts/run-tests.sh
```

Pass extra pytest args as needed, for example:

```bash
bash scripts/run-tests.sh tests/test_auth.py -vv
```

**Before manual play** in a dev session, run the suite (or at least the areas you touched).

## Coverage policy

- **Required:** **100%** line and **branch** coverage on **measured** packages, enforced by `--cov-fail-under=100`.
- **Omitted from the gate** (still in the tree; can be included later):
  - `galactic_wrestling/__main__.py` — thin entry shim.
  - `galactic_wrestling/ui/screens.py` — Textual event wiring; too large to fairly demand line coverage without a dedicated pilot suite.

**If you change omit rules**, update this doc and [docs/README.md](README.md) so future sessions know why.

### When you add UI tests

If you add substantial **Textual pilot** tests for `screens.py`, you may:

1. Remove `ui/screens.py` from `[tool.coverage.run] omit`, and
2. Keep or raise the fail-under threshold once coverage is stable.

## Test style

- Use the **`isolated_data_dir`** fixture (see `tests/conftest.py`) for any test that touches auth or storage so parallel runs and CI do not clobber `~/.galactic-wrestling`.
- Prefer **clear names** (`test_login_wrong_password`) and **one behavioral assertion group** per test where possible.
- **New modules** should land with tests in the same change unless explicitly documented as prototype.

## Imports

Tests use `pythonpath = ["src"]` and **`--import-mode=importlib`** to reduce import-order quirks with coverage.
