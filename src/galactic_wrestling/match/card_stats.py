"""Deterministic numeric attributes for :class:`~galactic_wrestling.cards.CardDef` in matches."""

from __future__ import annotations

import hashlib

from galactic_wrestling.cards import CardDef
from galactic_wrestling.match.model import MatchCard


def match_card_from_card_def(d: CardDef) -> MatchCard:
    """Map a card definition to runtime stats (stable across machines for the same ``id``)."""
    h = hashlib.sha256(d.id.encode()).digest()
    cost = h[0] % 4
    offense = 1 + (h[1] % 8)
    defense = 1 + (h[2] % 8)
    heat = h[3] % 3
    return MatchCard(d.id, d.name, cost, offense, defense, heat, None)
