# Plan 02 — AI opponents and single-player

**Status:** Roster seeding and **Single player** menu listing opponents are **implemented**; **match play** is still future work.

## Goals

1. Provide **six AI opponent wrestlers** — **one per** `Archetype` — for single-player matches.
2. Assign **random** ring name, **alignment**, and **gimmick** at creation (no duplicate archetypes in the AI pool).
3. **Seed** the roster:
   - When the **game starts** (`GalacticApp.on_mount` calls `ensure_ai_opponents()`).
   - During **`scripts/bootstrap.sh`** (`python -m galactic_wrestling.ai_opponents`).
   - If the folder is empty or individual archetypes were removed, only **missing** archetypes are created.
4. Expose **Single player** on the main menu: list AI opponents; combat is a stub until the match engine exists.

## Implementation

| Piece | Location |
|-------|-----------|
| Generation + persistence | `src/galactic_wrestling/ai_opponents.py` |
| App startup hook | `src/galactic_wrestling/app.py` (`ensure_ai_opponents()` after `ensure_data_tree()`) |
| Bootstrap hook | `scripts/bootstrap.sh` |
| CLI entry | `python -m galactic_wrestling.ai_opponents` |
| UI | `SinglePlayerScreen` in `src/galactic_wrestling/ui/screens.py` |

## On-disk layout

- `data_dir()/ai_opponents/<wrestler-uuid>.json` — same `Wrestler` JSON as player saves; **no** `player_id` wrapper.

## Tests

- `tests/test_ai_opponents.py` — empty list, full ensure, idempotency, refill after delete, `_random_name` edge cases.

## Follow-ups

1. **Match engine** — Select AI opponent, run turns using shared rules with PVP.
2. **Difficulty / AI decks** — Optionally skew AI decks or stats by archetype.
3. **Regenerate AI roster** — Menu or CLI flag to rebuild all six (destructive).
4. **Pilot tests** — Optional Textual tests for `SinglePlayerScreen` if coverage for `screens.py` is desired.
