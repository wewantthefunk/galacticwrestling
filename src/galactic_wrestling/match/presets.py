from __future__ import annotations

from galactic_wrestling.match.model import MatchCard

# Ten cards per deck; mirrored totals for quick balance tests.
_TEST_CARDS: tuple[MatchCard, ...] = (
    MatchCard("m1", "Jab", 1, 4, 3, 0),
    MatchCard("m2", "Block", 1, 2, 6, 0),
    MatchCard("m3", "Clothesline", 2, 6, 2, 0),
    MatchCard("m4", "Slam", 2, 5, 4, 0),
    MatchCard("m5", "Rest Hold", 1, 1, 7, 0),
    MatchCard("m6", "Dropkick", 2, 7, 1, 0),
    MatchCard("m7", "Elbow", 1, 3, 5, 0),
    MatchCard("m8", "Suplex", 2, 6, 3, 0),
    MatchCard("m9", "Taunt", 0, 2, 2, 1),
    MatchCard("m10", "Finisher", 3, 8, 0, 0),
)


def mirror_decks() -> tuple[list[MatchCard], list[MatchCard]]:
    """Two identical 10-card decks (equal total card value)."""
    cards = list(_TEST_CARDS)
    return cards.copy(), cards.copy()
