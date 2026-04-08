from __future__ import annotations

import random

from galactic_wrestling.match.deck_builder import build_match_decks, card_value
from galactic_wrestling.models import Alignment, Archetype, Wrestler, utc_now_iso


def _w(name: str, arch: Archetype) -> Wrestler:
    return Wrestler(
        id="00000000-0000-0000-0000-000000000001",
        name=name,
        archetype=arch,
        alignment=Alignment.BABYFACE,
        gimmick_id="showman",
        created_at=utc_now_iso(),
        updated_at=utc_now_iso(),
    )


def test_card_value() -> None:
    from galactic_wrestling.match.model import MatchCard

    c = MatchCard("x", "N", 2, 3, 4, -1)
    assert card_value(c) == 2 + 3 + 4 + 1


def test_build_match_decks_equal_totals_and_length() -> None:
    p = _w("Hero", Archetype.FLYER)
    ai = _w("Bot", Archetype.JOBBER)
    rng = random.Random(42)
    pd, ad = build_match_decks(p, ai, rng)
    assert len(pd) == len(ad) == 10
    sp = sum(card_value(c) for c in pd)
    sa = sum(card_value(c) for c in ad)
    assert sp == sa


def test_build_match_decks_deterministic_rng() -> None:
    p = _w("A", Archetype.GIANT)
    ai = _w("B", Archetype.COMEDY)
    a1, b1 = build_match_decks(p, ai, random.Random(99))
    a2, b2 = build_match_decks(p, ai, random.Random(99))
    assert [c.offense for c in a1] == [c.offense for c in a2]
    assert [c.name for c in a1] == [c.name for c in a2]
