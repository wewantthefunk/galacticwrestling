"""Build equal-value 10-card :class:`~galactic_wrestling.match.model.MatchCard` decks for two wrestlers."""

from __future__ import annotations

import random

from galactic_wrestling.cards import starter_deck
from galactic_wrestling.match.card_stats import match_card_from_card_def
from galactic_wrestling.match.model import MatchCard
from galactic_wrestling.match.presets import CANONICAL_TEN
from galactic_wrestling.models import Wrestler


def card_value(c: MatchCard) -> int:
    return c.cost + c.offense + c.defense + abs(c.heat)


def _pool_for_wrestler(w: Wrestler) -> list[MatchCard]:
    return [match_card_from_card_def(d) for d in starter_deck(w.archetype)]


def build_match_decks(
    player: Wrestler, ai: Wrestler, rng: random.Random
) -> tuple[list[MatchCard], list[MatchCard]]:
    """Ten cards per side with identical total stats (canonical multiset), names from each pool.

    The strongest ten cards from each archetype pool (by :func:`card_value`) are paired with a
    shuffled ordering of the ten canonical stat blocks so both decks sum to the same totals.
    """
    p_pool = _pool_for_wrestler(player)
    a_pool = _pool_for_wrestler(ai)
    p_ranked = sorted(p_pool, key=card_value, reverse=True)[:10]
    a_ranked = sorted(a_pool, key=card_value, reverse=True)[:10]
    canon_sorted = sorted(CANONICAL_TEN, key=card_value, reverse=True)
    perm = list(range(10))
    rng.shuffle(perm)
    player_deck: list[MatchCard] = []
    ai_deck: list[MatchCard] = []
    for rank in range(10):
        template = canon_sorted[perm[rank]]
        pr = p_ranked[rank]
        ar = a_ranked[rank]
        player_deck.append(
            MatchCard(
                pr.id,
                pr.name,
                template.cost,
                template.offense,
                template.defense,
                template.heat,
                template.special,
            )
        )
        ai_deck.append(
            MatchCard(
                ar.id,
                ar.name,
                template.cost,
                template.offense,
                template.defense,
                template.heat,
                template.special,
            )
        )
    return player_deck, ai_deck
