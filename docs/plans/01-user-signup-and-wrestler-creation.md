# Plan 01 — User signup and wrestler creation

**Status:** Core behaviour **implemented**; this document records the **agreed design** and **follow-ups** for later sessions.

## Goals

1. **Signup** — Create a local account with unique login name and password.
2. **Login** — Strict password every time; login name is also the display name.
3. **Session** — After login, access main menu actions for this account only.
4. **Wrestler roster** — Up to **five** wrestlers per account; delete frees a slot; rename allowed.
5. **Create wrestler** — Pick name, archetype (immutable after save), starting alignment, gimmick; see **live starter deck preview** (basic + archetype cards).
6. **Persistence** — JSON on disk, one folder tree per player id; documented in [Design patterns](../design-patterns.md).

## Decisions (locked)

| Topic | Decision |
|-------|----------|
| Max wrestlers | 5 per account |
| Archetype change | Not allowed after creation |
| Alignment change | Allowed later in-game (not necessarily implemented yet) |
| Starter deck | Same **basic** cards for everyone + **5–7** archetype-specific cards |
| Creation UX | Single screen; tab between controls; preview updates when archetype/gimmick changes |
| PVP prerequisite | Head-to-head uses **two different accounts**; each picks their own wrestler |

## On-disk shape (summary)

- `registry.json` — Maps normalized login name → `player_id`.
- `players/<player_id>/account.json` — `login_name`, `password_hash`, `created_at`, etc.
- `players/<player_id>/wrestlers/<uuid>.json` — Wrestler record (`name`, `archetype`, `alignment`, `gimmick_id`, timestamps).

Tests use `GALACTIC_WRESTLING_DATA_DIR` so CI and developers do not touch real saves.

## Implementation checklist (for maintainers)

- [x] Signup with duplicate-name rejection (case-insensitive).
- [x] Login with Argon2 verification; generic error on failure.
- [x] Logout clears in-app session and returns to login.
- [x] Wrestler list, create, rename, delete with slot cap.
- [x] Create screen: `Select` for archetype, alignment, gimmick; deferred preview so Textual `Select` values are valid on first paint.
- [x] Head-to-head flow: two logins, wrestler pick, stub match message.

## Follow-ups (future sessions)

1. **Alignment changes in-game** — Story/events or menu action; persist updated `alignment` on wrestler JSON.
2. **Gimmick depth** — Tie `gimmick_id` to Heat rules, finishers, and rivalry hooks when match engine exists.
3. **Deck snapshot** — Today starter deck is **derived** from archetype; if decks diverge after rewards, consider storing deck state or diffs in save files.
4. **UI coverage** — Optional Textual pilot tests for `screens.py` if we want coverage metrics to include the full UI layer.
5. **Accessibility** — Document keybindings and ensure Esc/back paths stay predictable as screens grow.

## Related code

| Area | Location |
|------|-----------|
| Auth | `src/galactic_wrestling/auth.py` |
| Wrestler storage | `src/galactic_wrestling/storage.py` |
| Models | `src/galactic_wrestling/models.py` |
| Cards / starter deck | `src/galactic_wrestling/cards.py` |
| Gimmicks list | `src/galactic_wrestling/gimmicks.py` |
| UI | `src/galactic_wrestling/ui/screens.py` |
| Tests | `tests/test_auth.py`, `tests/test_storage.py`, … |
