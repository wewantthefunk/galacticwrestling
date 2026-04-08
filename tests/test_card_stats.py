from __future__ import annotations

from galactic_wrestling.cards import CardDef
from galactic_wrestling.match.card_stats import match_card_from_card_def


def test_match_card_from_card_def_stable() -> None:
    d = CardDef("basic_punch", "Punch")
    a = match_card_from_card_def(d)
    b = match_card_from_card_def(d)
    assert a == b
    assert a.id == "basic_punch"
    assert a.name == "Punch"
    assert 0 <= a.cost < 4
    assert 1 <= a.offense <= 8
    assert 1 <= a.defense <= 8
    assert 0 <= a.heat < 3
