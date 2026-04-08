from __future__ import annotations

import pytest

from galactic_wrestling import cards
from galactic_wrestling.cards import format_starter_deck_preview, starter_deck
from galactic_wrestling.models import Archetype


def test_basic_card_count() -> None:
    assert len(cards.BASIC_CARDS) == 8


@pytest.mark.parametrize(
    "arch",
    list(Archetype),
)
def test_each_archetype_has_starter_deck(arch: Archetype) -> None:
    deck = starter_deck(arch)
    assert len(deck) == len(cards.BASIC_CARDS) + len(cards.ARCHETYPE_CARDS[arch])
    assert all(c in deck for c in cards.BASIC_CARDS)


def test_starter_deck_unknown_archetype_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    reduced = {k: v for k, v in cards.ARCHETYPE_CARDS.items() if k != Archetype.GIANT}
    monkeypatch.setattr(cards, "ARCHETYPE_CARDS", reduced)
    with pytest.raises(ValueError, match="Unknown archetype"):
        starter_deck(Archetype.GIANT)


def test_format_preview_contains_names() -> None:
    text = format_starter_deck_preview(Archetype.REGULAR)
    assert "Punch" in text
    assert "basic_punch" in text
