from __future__ import annotations

import random

import pytest

from galactic_wrestling.match.ai_policy import choose_ai_hand_index
from galactic_wrestling.match.engine import MatchState
from galactic_wrestling.match.model import MatchCard


def test_choose_ai_empty_hand_raises() -> None:
    s = MatchState(ai_hand=[], player_hand=[MatchCard("p", "P", 0, 1, 1, 0)])
    with pytest.raises(ValueError, match="empty"):
        choose_ai_hand_index(s, random.Random(0))


def test_choose_ai_empty_player_hand_random_index() -> None:
    s = MatchState(
        ai_hand=[
            MatchCard("a", "A", 0, 1, 1, 0),
            MatchCard("b", "B", 0, 2, 2, 0),
        ],
        player_hand=[],
    )
    rng = random.Random(0)
    idx = choose_ai_hand_index(s, rng)
    assert idx in (0, 1)


def test_choose_ai_prefers_better_expected_trade() -> None:
    # Player hand: one weak card. AI: high offense beats weak defense for damage dealt.
    pc = MatchCard("p", "P", 0, 1, 1, 0)
    good = MatchCard("g", "Good", 0, 9, 1, 0)
    bad = MatchCard("x", "Bad", 0, 1, 9, 0)
    s = MatchState(
        player_hand=[pc],
        ai_hand=[bad, good],
    )
    idx = choose_ai_hand_index(s, random.Random(0))
    assert idx == 1
