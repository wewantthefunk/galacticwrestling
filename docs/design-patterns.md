# Design and architecture

This document captures **patterns and boundaries** so future sessions stay consistent.

## Layout

- **`src/galactic_wrestling/`** — Installable package (Hatchling / `pyproject.toml`).
- **`tests/`** — Pytest suite; `conftest.py` holds shared fixtures (e.g. isolated data directory).
- **`scripts/`** — Shell helpers (`bootstrap.sh`, `run-tests.sh`); no business logic.

## Layering

1. **Domain / data** (`models.py`) — `Wrestler`, enums (`Archetype`, `Alignment`), JSON serialization helpers. No I/O.
2. **Rules data** (`cards.py`, `gimmicks.py`) — Immutable definitions and helpers (e.g. starter deck for an archetype). Easy to unit test.
3. **Persistence** (`config.py`, `auth.py`, `storage.py`) — Filesystem layout under `data_dir()`, registry, accounts, player wrestler JSON files. No UI imports.
4. **AI opponents** (`ai_opponents.py`) — Same `Wrestler` JSON shape as player wrestlers, stored under `data_dir()/ai_opponents/<uuid>.json`. Not tied to a `player_id`. `ensure_ai_opponents()` fills in missing archetypes (deterministic count: one per `Archetype`).
5. **Presentation** (`app.py`, `ui/screens.py`) — Textual `App` and `Screen` classes; call into auth, storage, and AI roster helpers.

**Rule of thumb:** New **game rules** and **save format** live in the middle layers; screens stay thin (gather input, show errors, call services).

## UI stack

- **Textual** for TUI: screens, focus, widgets (`Input`, `Select`, `ListView`, etc.).
- **Async smoke tests** use `app.run_test()` for minimal integration checks; full UI flows are not yet covered by line coverage (see [Testing and coverage](testing-and-coverage.md)).

## Persistence model

- **Registry** (`registry.json`) maps normalized login name → `player_id`.
- **Per player:** `players/<uuid>/account.json` (credentials and profile fields), `players/<uuid>/wrestlers/<wrestler-uuid>.json`.
- **AI opponents (global):** `ai_opponents/<wrestler-uuid>.json` — same schema as player wrestlers; used for single-player opposition.
- **Passwords:** Argon2 via `argon2-cffi` (hashes only on disk).

## Security and ergonomics

- Passwords are never logged; login failures use a **generic message** (no user enumeration).
- `GALACTIC_WRESTLING_DATA_DIR` overrides the data root for tests and portable setups.

## Adding features later

- **New card types / pools:** Extend `cards.py` and tests first; wire UI second.
- **Match engine:** Prefer a **pure module** (state + events) testable without Textual, then a thin adapter from PVP / single-player screens.
- **Networking (if ever):** Keep transport out of domain; same domain API as local PVP.
