# Game overview — Galactic Wrestling

## Elevator pitch

**Galactic Wrestling** is a **terminal-based** wrestling game using **ASCII (and simple TUI widgets)** at most. Wrestlers fight **head to head** in a **deckbuilder** framework: winning matches earns **better cards** and progression.

## Design pillars

1. **Readable in the terminal** — No required GUI; clarity over flash.
2. **Deckbuilding** — Matches are driven by a deck of moves (cards); the deck evolves over time.
3. **Identity** — Wrestlers have **archetype**, **alignment** (babyface / heel), and **gimmick**; archetype is fixed, alignment can change in play.
4. **Multiple players on one machine** — Separate accounts and save data; optional **local head-to-head (PVP)** between two logged-in players.

## Player-facing concepts (current and planned)

### Accounts

- **Login name** doubles as **display name** (no separate “screen name” in v1).
- **Strict password** on every session (no remembered auto-login).
- Data lives under a per-machine directory (see [Setup and run](setup-and-run.md)).

### Wrestlers

- Each account can hold up to **five** wrestlers (slots freed by delete).
- **Archetypes** (fixed after creation): Giant, Flyer, Jobber, Flashy, Comedy, Regular.
- **Starting alignment**: Babyface or Heel (changeable later in the game).
- **Gimmick**: Flavor and future hooks (Heat, special moves, nicknames, arch-enemies, etc.).
- **Starter deck**: Shared **basic** move cards plus **5–7 archetype-specific** cards (same basic package for everyone).

### Modes

- **Single-player** — You play against **AI opponent** wrestlers (one per archetype). The **match engine** is still a stub; the main menu lists available AI opponents. See [Plan 02](plans/02-ai-opponents-single-player.md).
- **Head-to-head (local PVP)**: two different accounts log in, each picks a wrestler; match resolution is still to be built on top of this flow.

### AI opponents (single-player)

- Stored **outside** player accounts under `ai_opponents/` in the data directory (see [Design patterns](design-patterns.md)).
- The game ensures **six** AI wrestlers — **one per archetype** — with **random** name, **alignment**, and **gimmick** at creation time.
- **Seeding:** `ensure_ai_opponents()` runs when the app starts (if any archetype is missing, it creates only the missing ones). **`scripts/bootstrap.sh`** also runs `python -m galactic_wrestling.ai_opponents` after install so a fresh venv gets a roster without launching the UI.

## What is implemented vs planned

| Area | Status (high level) |
|------|---------------------|
| Signup / login / logout | Implemented |
| Wrestler CRUD, creation UI with live deck preview | Implemented |
| AI opponent roster (6, one per archetype) | Implemented |
| Card definitions (basic + archetype) | Data in code; combat not wired |
| Match / deck combat | Stub |
| Card rewards, meta progression | Planned |

This doc is the **north star** for features; detailed slices live under [plans/](plans/).
