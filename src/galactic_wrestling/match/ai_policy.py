"""Heuristic AI card choice using only public match state (fair play)."""

from __future__ import annotations

import random

from galactic_wrestling.match.engine import MatchState, clash_damage


def choose_ai_hand_index(state: MatchState, rng: random.Random) -> int:
    """Pick an AI hand index maximizing expected ``damage_to_player - damage_to_ai`` vs a random human card.

    The human hand is treated as uniformly random (no peek at the card the player will play).
    """
    if not state.ai_hand:
        raise ValueError("AI hand is empty.")
    if not state.player_hand:
        return rng.randrange(len(state.ai_hand))
    scores: list[tuple[float, int]] = []
    for i, ai_card in enumerate(state.ai_hand):
        total = 0.0
        for player_card in state.player_hand:
            dmg_to_player, dmg_to_ai = clash_damage(player_card, ai_card)
            total += dmg_to_player - dmg_to_ai
        scores.append((total / len(state.player_hand), i))
    best = max(s[0] for s in scores)
    best_indices = [i for s, i in scores if s == best]
    return rng.choice(best_indices)
