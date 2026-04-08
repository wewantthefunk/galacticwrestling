# Plan 04 — Match integration and remaining systems

**Depends on:** [Plan 03](03-single-player-match-flow-and-engine.md) (design), [Plan 02](02-ai-opponents-single-player.md) (AI roster).

**Current code:** `galactic_wrestling.match` (`MatchState`, `clash_damage`, `MatchCard`, `mirror_decks`) is a **playable prototype** with two-lane damage, 10-card decks, 5-card hands, health, discard/recycle. Run: `python -m galactic_wrestling.match`.

This plan covers **everything left** to turn that core into the full **single-player experience** described in Plan 03: menus, Textual UI, economy (heat + market), specials, real card data, meta (W/L), and AI policy.

---

## 1. Scope summary

| Area | Status today | This plan delivers |
|------|----------------|-------------------|
| Two-lane clash + `MatchState` | Done (`match/`) | Extend only where needed (heat pool, market, specials hooks). |
| Pre-match wizard | Not built | Gating, pick wrestler, random/specific AI, location, stipulation. |
| Textual match UI | Not built | Split panels, hands, logs, market row, forfeit. |
| Heat as currency | Not in engine | Player/AI heat pools; gain/spend rules tied to cards. |
| Market | Not in engine | Common row + deck + buy flow; forget purchases after match. |
| `special` on cards | Field exists on `MatchCard`; unused | Structured effects or v1 no-ops + log line. |
| Decks from real wrestlers | `cards.py` + archetype starters | Map `CardDef` → `MatchCard` with full attributes; equal-value deck builder. |
| W/L record | Not persisted | Minimal stats file per account (or per wrestler). |
| AI play | Random in `match/__main__.py` | Heuristic `choose_card` using public state only. |

---

## 2. Phase A — Pre-match flow (Textual)

1. **Guard:** If `storage.count_wrestlers(player_id) < 1`, block entry and notify (link to Manage wrestlers).
2. **Screen sequence** (stack or wizard):
   - Select **your wrestler** (`list_wrestlers`).
   - **AI:** `Random AI opponent` vs **list** from `list_ai_wrestlers()` (name + archetype).
   - **Location** enum: regular ring, cage, parking lot, anywhere in arena.
   - **Stipulation** enum: straight rules, anything goes, count out, tap out.
3. **Start match:** Build `MatchState` (or a thin `MatchSession` wrapper) with chosen participants and pass **modifier context** (location/stipulation) into the engine or UI-only for cosmetics until modifiers are numeric.

**Deliverable:** User can reach a “Ready to fight” state with all choices stored; optional stub that immediately returns to menu until Phase B exists.

---

## 3. Phase B — Deck and card pipeline

1. **Source of truth:** Existing `CardDef` / archetype lists in `cards.py` (and future data files).
2. **Mapping:** `CardDef` → `MatchCard`: assign **cost, offense, defense, heat, special** (extend `CardDef` or maintain a parallel table keyed by `id`).
3. **Deck construction:**
   - Build **10-card** decks for player and AI from the wrestlers’ archetype-appropriate pools.
   - **Equal total value** between sides (sum of a defined value function, or normalize after sampling).
4. **AI deck:** Same rules as player; AI wrestler archetype drives its pool.

**Deliverable:** Function e.g. `build_match_decks(player_wrestler, ai_wrestler) -> tuple[list[MatchCard], list[MatchCard]]` with tests (deterministic RNG).

---

## 4. Phase C — Heat and market (engine + rules)

1. **Heat pools:** Separate integers for player and AI; starting value (e.g. 0) and **when** heat changes (on play, on hit, card text).
2. **Card `heat` attribute:** Define whether it means **income**, **cost to play**, or **toward purchases** — pick one primary meaning for v1 and document in `docs/game-rules.md`.
3. **Market:**
   - **Common** face-up row (size N); **market deck** refill.
   - **Buy:** Pay heat ≥ card **cost**; card goes to **discard** (then shuffle rules match existing `MatchState` pipeline).
   - **End of match:** Discard all in-match deck mutations; next match uses Phase B builders only.

**Deliverable:** Extend `MatchState` (or a `MatchStateV2`) with `market_row`, `market_deck`, `player_heat`, `ai_heat`, and a **market phase** after clash resolution each round (or separate step — lock order in rules doc).

---

## 5. Phase D — Specials

1. **Representation:** Prefer **structured** effects (`enum` + parameters) on `MatchCard` or a sidecar dict for testing and AI.
2. **Examples for v1:** “+1 defense next round”, “gain 1 heat”, “opponent loses 1 heat” — small set only.
3. **Application order:** After clash damage, before or after market (specify once).

**Deliverable:** At least one working special in tests; AI ignores or uses simple scoring for specials.

---

## 6. Phase E — Textual `MatchScreen`

1. **Layout:** Two columns — player / AI (name, health, **heat**, hand count); **two scroll regions** for parallel fight log (or prefixed lines).
2. **Turn loop:** Select card from hand (ListView or buttons) → confirm; AI chooses via heuristic; reveal + log clash results; market UI if Phase C is in.
3. **Controls:** Forfeit (with confirm), Esc back to menu post-match.
4. **Wire:** `MainMenu` → Single player flow → `MatchScreen`; on outcome, show result and update W/L.

**Deliverable:** Play one full match against AI in the TUI without using `python -m galactic_wrestling.match`.

---

## 7. Phase F — AI opponent policy

Replace random play in demos with **`choose_play(hand, state) -> index`**:

- Score each legal card by expected damage dealt minus damage taken (using same `clash_damage` logic).
- Add bonuses for heat/market if Phase C exists.
- No information the human would not have in the same position.

**Deliverable:** Pure function under `tests/` with fixed seeds.

---

## 8. Phase G — Meta (W/L)

1. Persist **wins / losses** (per account or per wrestler — align with Plan 03 §9).
2. Update after match outcome in `MatchScreen` teardown or callback.

**Deliverable:** `stats.json` (or equivalent) + tests with isolated data dir.

---

## 9. Testing and coverage

- Keep **100%** line/branch coverage on **non-UI** modules (`match/` extensions, deck builders, AI choose).
- `ui/screens.py` remains **omitted** from the coverage gate unless you add Textual pilot tests (see [Testing and coverage](../testing-and-coverage.md)).
- Add integration test: build decks → run `MatchState` until terminal outcome with scripted choices.

---

## 10. Suggested implementation order

1. **B** — Deck pipeline from real wrestlers (unblocks meaningful playtests).
2. **A** — Pre-match wizard (navigation shell).
3. **E** — Minimal `MatchScreen` wired to **B** (no market yet; heat frozen at 0 if needed).
4. **F** — AI heuristic for card choice.
5. **C** — Heat + market.
6. **D** — Specials.
7. **G** — W/L persistence.

Adjust order if you prefer “feel” (E) before deck fidelity (B) by using `mirror_decks()` temporarily.

---

## 11. Files likely to touch

| Area | Files / new modules |
|------|---------------------|
| Wizard | `ui/screens.py` or `ui/single_player_wizard.py` |
| Deck build | `match/decks.py` or `galactic_wrestling/deck_builder.py` |
| Engine extensions | `match/engine.py`, `match/model.py` |
| Rules doc | `docs/game-rules.md` (heat, market order, specials) |
| Stats | `storage.py` or `stats.py` |
| App entry | `app.py`, menu handlers |

---

*This plan is the roadmap for the “last part” after the match prototype: integration, economy, presentation, and persistence.*
