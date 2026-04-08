"""Run a quick random simulation (stdout). For manual smoke testing."""

from __future__ import annotations

import random

from galactic_wrestling.match.engine import MatchState
from galactic_wrestling.match.model import MatchOutcome
from galactic_wrestling.match.presets import mirror_decks


def _run() -> None:
    rng = random.Random()
    pd, ad = mirror_decks()
    state = MatchState.from_decks(pd, ad, rng=rng)
    round_num = 0
    while state.outcome() == MatchOutcome.ONGOING and round_num < 100:
        if not state.player_hand or not state.ai_hand:
            break
        pi = rng.randrange(len(state.player_hand))
        ai = rng.randrange(len(state.ai_hand))
        r = state.play_round(pi, ai)
        round_num += 1
        print(
            f"R{round_num}: {r.player_card.name} vs {r.ai_card.name} | "
            f"dmg P={r.damage_to_player} AI={r.damage_to_ai} | "
            f"HP P={r.player_health_after} AI={r.ai_health_after}"
        )
    print("Outcome:", state.outcome())


if __name__ == "__main__":  # pragma: no cover
    _run()
