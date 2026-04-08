# Plan 03 — Single-player match flow and engine (draft for review)

This plan turns your design notes into **phased work**: menus and gating first, then a **vertical slice** of the match (simultaneous play → resolve → effects), then locations/stipulations/market depth, then persistence and polish.

---

## 1. Goals (what “done” means for v1)

1. **Gating:** Player cannot open the single-player flow until they have **at least one** wrestler on their account.
2. **Pre-match flow:** After choosing single player → **AI choice** (random or specific) → **location** → **stipulation** → **start match**.
3. **Match core:** **Both play, then resolve** each round: each side commits one card **simultaneously** (then reveal). Each card contributes **both offense and defense**. Two **cross-comparisons** drive the turn (see §3.2). Then apply **secondary effects** (card specials, heat, etc.).
4. **Deck model for the match:** Start with **10-card decks** and **5-card hands**; **purchases from a common market** add cards to the deck **for the rest of this match only**; **after the match, purchased cards are forgotten** (next match starts fresh from the normal starter construction rules you already have, or a defined “match start” deck—see §5).
5. **AI:** **Simple priority** policy (heuristics), **no hidden illegal moves**, same rules as the player.
6. **UI:** **Split view** — wrestlers **side by side**, **parallel scrolling** action log (or two columns of log—implementation detail).
7. **Meta for now:** Record **W/L** only (per account or per wrestler—decide in §8).

Non-goals for first slice (unless you promote them): networked play, PVP rule parity with full card editor, long-term collection from market cards across matches.

---

## 2. Pre-match flow (screens / steps)

| Step | Player action | Notes |
|------|----------------|--------|
| 0 | **Guard** | If `count_wrestlers(player) == 0`, show message and return to main menu (or link to Manage wrestlers). |
| 1 | **Pick your wrestler** | From player roster (max 5). |
| 2 | **Pick AI** | **“Random AI opponent”** (uniform among the six archetype AIs, or weighted later) **or** pick a **specific** AI from `list_ai_wrestlers()`. |
| 3 | **Location** | `regular ring` · `cage match` · `parking lot match` · `anywhere in the arena` — v1 can store as an **enum** and apply **modifiers** via a small table (even +0 across the board until you define differences). |
| 4 | **Stipulation** | `straight rules` · `anything goes` · `count out` · `tap out` — same: enum + modifier table (or cosmetic-only in slice 1). |
| 5 | **Start** | Build initial match state and push **MatchScreen**. |

**Open decision:** Do locations/stipulations affect **only** numeric modifiers, or also **which cards appear in the market**? *Default for plan:* modifiers only (simpler).

---

## 3. Match structure (round loop)

### 3.1 Phases per round (conceptual)

1. **Upkeep** (optional v1): tick durations, decay temp bonuses.
2. **Simultaneous choice:** Each side selects **one card from hand** for this round’s clash (or pass/market-only later if added).
3. **Reveal & resolve clash** using the **two-lane model** in §3.2.
4. **Apply secondary effects** from cards (next-round buffs, heat, scripted specials, etc.) after health/damage from the clash is applied.
5. **Market phase (if in scope this slice):** Spend **heat** to buy from **common market**; purchased card goes to **discard** or **bottom of deck** (define).
6. **Draw** to hand size **5** (if deck allows; handle empty deck).
7. **Check end:** Win condition (§6).

### 3.2 Simultaneous clash resolution (locked)

Each played card has **offense** and **defense**. There are **two independent comparisons**, each pairing one stat on one card with the other stat on the other card:

| Lane | Comparison | Meaning |
|------|------------|--------|
| **Your attack lane** | **Your offense** vs **opponent’s defense** | Determines whether **you** get through and **deal damage** (you “win” this lane when your offense beats their defense—exact strict/≥ rule in implementation). |
| **Your defense lane** | **Opponent’s offense** vs **your defense** | Determines whether **you block** or **take damage**. If **your defense is lower than their offense**, **you suffer damage** on this lane. |

**Overall turn goal (player perspective):** **Win both lanes** — succeed on **offense** (damage them) **and** on **defense** (block their attack, no damage to you). That is the “full” winning exchange for the round.

**Symmetric outcomes:**

- **Both players can lose on defense:** Each side’s defense is **insufficient** vs the other’s offense → **both take damage** in the same round.
- **Both players can win on defense:** Each side’s defense **holds** vs the other’s offense → **neither takes damage from the defense lane**; apply any **regain health** (or similar) from card **special** text or stipulation when both “win” defense (exact rule: tie to specials / base heal—TBD in balance pass).

The implementation should run exactly **two comparisons** per round: **A.offense vs B.defense** and **B.offense vs A.defense**, then derive **damage to A**, **damage to B** (and any heal/regain from specials), and feed **special** triggers.

*Tie-breaking and exact damage amounts* (e.g. difference of stats, minimum 1 damage, zero on tie) stay in §12 / `docs/game-rules.md` when balancing.

---

## 4. Card model (attributes)

Five attributes on every card:

| Attribute | Role |
|-----------|------|
| **cost** | Heat spent to **buy this card from the market** (if applicable). |
| **offense** | Used in **your attack lane** (your offense vs their defense). |
| **defense** | Used in **your defense lane** (their offense vs your defense). |
| **heat** | **Currency** generated or spent toward purchases (clarify: is “heat” *only* player pool, or also on card as “reward heat”?). |
| **special** | Text or structured token for **exceptions** (bonus next round, ignore tie, extra draw, etc.). |

**Starter deck equality:** For the match start, both sides get **decks of equal total value** (sum of a defined “card value” function—e.g. `offense + defense + cost` or a dedicated `value` field). Existing `CardDef` in code will need **extension** or a **MatchCard** type for runtime instances.

**Market:** Common row of face-up cards; buying removes from market and shuffles/refills from a **market deck** (define size and refill rule).

**Special:** Prefer **structured effects** (enum + args) in code for AI and tests; free text only for UI labels in early drafts.

---

## 5. Decks and persistence (within match vs between matches)

- **Match start:** Build **10-card** decks from a **seed pool** (could be wrestler’s **starter deck** from existing `cards.py` **trimmed/reweighted** to 10 with equal total value vs AI—needs a small **deck builder** function).
- **Hand:** **5** cards; draw rules on round start/end as you specified.
- **During match:** Purchases **append** or go to **discard** and eventually shuffle—pick one pipeline (standard deckbuilder: draw pile + discard + shuffle when empty).
- **After match:** Discard all **in-match** deck mutations; **W/L** persists (see §8).

**Open decision:** Should the **10-card** starter come from the **same** archetype packages you already have (subset), or a **dedicated “match starter”** list for balance? *Default:* derive from existing card defs with a **normalization** step to hit equal value.

---

## 6. Win / loss / resources

You listed **health** and **heat** in effects. Define for v1:

- **Starting health** (e.g. 20? 30?)
- **Heat** pool per player: starts at **0** or **X**; cards add/spend it.
- **Win conditions** tied to stipulation, e.g.:
  - **Straight rules:** health to 0, or most health after N rounds.
  - **Tap out:** accumulate **submission** points?
  - **Count out:** miss playing a valid card N times?

*Recommendation:* Start with **one** win condition for the first playable build (e.g. **reduce opponent health to 0**), map stipulations as **modifiers** to damage/effects until you add mode-specific win logic.

---

## 7. AI (simple priorities, fair play)

- **Information:** AI decisions use **only** legal options from **public state** (its hand, both known pools, market, discard piles if public, etc.). **No peek** at player’s facedown choice before commit if the human commits first—**simultaneous reveal** avoids this.
- **Policy (examples):** Evaluate both lanes (offense vs their likely defense, your defense vs their likely offense—use expected card or heuristic).
  - Prefer cards that **win both lanes** when possible, or trade off damage dealt vs damage taken.
  - If low health → prioritize **defense** or **heal** specials.
  - If can **lethal** on offense lane → consider high **offense** plays.
  - Market: buy if **high value-per-heat** and spare heat.
- Implement as a **scoring function** over legal actions; keep **unit-testable** pure function `choose_action(state, rng)`.

---

## 8. UI layout (Textual)

- **Top or sides:** Two columns — **Player wrestler** (name, health, heat, hand count) | **AI wrestler** (same).
- **Center / bottom:** **Two synchronized vertical logs** or **one log with two prefixed columns** — your call; “parallel scrolling” suggests **two `RichLog`/`Log` widgets** side by side or **one log with `[YOU]` / `[AI]`** tags.
- **Hand:** Row of **selectable** card summaries (off/def/cost) and confirm button for the round.
- **Escape:** Forfeit / back with confirm.

---

## 9. Persistence (W/L)

- Store minimal record, e.g. `players/<id>/stats.json` or embedded in `account.json`: `{ "wins": n, "losses": m }` **or** per-wrestler `{ wrestler_id: { "w":, "l": } }`.
- **Open decision:** Global per account vs per wrestler. *Default:* per **account** for v1 (simplest).

---

## 10. Implementation phases (suggested order)

| Phase | Deliverable |
|-------|-------------|
| **P0** | Gating + wizard screens: wrestler → AI (random/specific) → location → stipulation → stub “Start” that shows summary and exits. |
| **P1** | **Match state** module (pure Python): round loop, simultaneous choices, **two-lane** resolve (§3.2), health/heat, no market yet. **Prototype:** `galactic_wrestling.match` (`clash_damage`, `MatchState`, `mirror_decks`); run `python -m galactic_wrestling.match` for a random simulation. |
| **P2** | **Card schema** extension + **10/5** deck/hand + build equal-value starters from existing defs. |
| **P3** | **Market** + purchase + discard/shuffle; end-of-match reset. |
| **P4** | **AI** heuristic + tests. |
| **P5** | **Textual MatchScreen** split view + logs + hand UI. |
| **P6** | **W/L** persistence + location/stipulation modifiers (or cosmetics first). |

---

## 11. Questions already answered by you (tracked)

- Block SP without ≥1 wrestler.
- Random or specific AI.
- Location + stipulation steps.
- **Simultaneous cards; each card has offense + defense; two cross-comparisons** (your off vs their def; their off vs your def); win both lanes for ideal turn; both can lose or both can win on defense; lower defense than opponent’s attack ⇒ damage.
- Deck unchanged *for the match* except purchases that are forgotten after match.
- 10 deck / 5 hand; cards have 5 attributes; market purchases; equal starting value.
- Simple AI priorities; no hidden cheating.
- Split UI + parallel action feed.
- W/L rewards; purchases forgotten next game.

---

## 12. Items to confirm before coding (quick checklist)

1. **Strict inequalities:** e.g. offense “wins” vs defense on `>`, `>=`, or margin-based damage (difference = damage)?
2. **Ties** on a lane: no damage, both damage, or special-only?
3. **“Regain health” when both win defense:** fixed amount, card **special**, or stipulation?
4. **Market timing:** End of round only, or separate phase?
5. **Heat:** Starting value and whether card “heat” attribute is **income**, **cost**, or both.
6. **Starting health** and base damage per winning lane.
7. **Stipulation/location:** Modifier-only for v1, or cosmetic-only first?

---

*After you review, we can lock §12, add a short `docs/game-rules.md` for the resolution table, and split tickets per phase.*
