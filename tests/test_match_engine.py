from __future__ import annotations

import random

import pytest

from galactic_wrestling.match.engine import HAND_SIZE, MatchState, clash_damage
from galactic_wrestling.match.model import MatchCard, MatchOutcome, RoundResult
from galactic_wrestling.match.presets import mirror_decks


def test_clash_damage_both_lanes() -> None:
    p = MatchCard("p", "P", 0, 6, 4, 0)
    a = MatchCard("a", "A", 0, 5, 3, 0)
    # P off 6 > A def 3 -> 3 dmg to AI; A off 5 > P def 4 -> 1 dmg to player
    assert clash_damage(p, a) == (1, 3)


def test_clash_damage_ties_no_damage() -> None:
    p = MatchCard("p", "P", 0, 3, 5, 0)
    a = MatchCard("a", "A", 0, 5, 3, 0)
    assert clash_damage(p, a) == (0, 0)


def test_clash_damage_strict_not_equal() -> None:
    p = MatchCard("p", "P", 0, 5, 5, 0)
    a = MatchCard("a", "A", 0, 5, 5, 0)
    assert clash_damage(p, a) == (0, 0)


def test_match_card_json_roundtrip() -> None:
    c = MatchCard("x", "N", 1, 2, 3, 4, "s")
    assert MatchCard.from_json(c.to_json()) == c
    assert MatchCard.from_json({**c.to_json(), "special": ""}).special is None


def test_from_decks_opens_hands() -> None:
    pd, ad = mirror_decks()
    s = MatchState.from_decks(pd, ad, rng=random.Random(0))
    assert len(s.player_hand) == HAND_SIZE
    assert len(s.ai_hand) == HAND_SIZE
    assert len(s.player_deck) == 5
    assert len(s.ai_deck) == 5


def test_play_round_applies_damage_and_outcome() -> None:
    pd, ad = mirror_decks()
    s = MatchState.from_decks(pd, ad, rng=random.Random(1))
    s.player_health = 5
    s.ai_health = 5
    r = s.play_round(0, 0)
    assert isinstance(r, RoundResult)
    assert r.player_health_after == max(0, 5 - r.damage_to_player)
    assert r.ai_health_after == max(0, 5 - r.damage_to_ai)


def test_play_round_invalid_index() -> None:
    pd, ad = mirror_decks()
    s = MatchState.from_decks(pd, ad, rng=random.Random(0))
    with pytest.raises(ValueError, match="player"):
        s.play_round(99, 0)
    with pytest.raises(ValueError, match="AI"):
        s.play_round(0, 99)


def test_play_round_when_over() -> None:
    pd, ad = mirror_decks()
    s = MatchState.from_decks(pd, ad, rng=random.Random(0))
    s.player_health = 0
    with pytest.raises(RuntimeError, match="already over"):
        s.play_round(0, 0)


def test_outcome_draw_both_zero() -> None:
    s = MatchState()
    s.player_health = 0
    s.ai_health = 0
    assert s.outcome() == MatchOutcome.DRAW


def test_outcome_player_wins() -> None:
    s = MatchState()
    s.ai_health = 0
    s.player_health = 1
    assert s.outcome() == MatchOutcome.PLAYER_WINS


def test_outcome_ai_wins() -> None:
    s = MatchState()
    s.player_health = 0
    s.ai_health = 1
    assert s.outcome() == MatchOutcome.AI_WINS


def test_play_round_empty_hand() -> None:
    s = MatchState(player_hand=[], ai_hand=[MatchCard("a", "A", 0, 1, 1, 0)])
    with pytest.raises(RuntimeError, match="empty hand"):
        s.play_round(0, 0)


def test_draw_stops_when_no_cards_anywhere() -> None:
    s = MatchState(player_hand=[], player_deck=[], player_discard=[], _rng=random.Random(0))
    s._draw_player_to(5)
    assert s.player_hand == []


def test_draw_ai_stops_when_no_cards_anywhere() -> None:
    s = MatchState(ai_hand=[], ai_deck=[], ai_discard=[], _rng=random.Random(0))
    s._draw_ai_to(5)
    assert s.ai_hand == []


def test_recycle_noop_when_discard_empty() -> None:
    s = MatchState(player_deck=[], player_discard=[], _rng=random.Random(0))
    s._recycle_player_discard()
    assert s.player_deck == []


def test_ai_recycle_and_draw() -> None:
    c = MatchCard("c", "C", 0, 1, 1, 0)
    s = MatchState(ai_deck=[], ai_hand=[], ai_discard=[c], _rng=random.Random(0))
    s._recycle_ai_discard()
    assert s.ai_deck == [c]
    s._draw_ai_to(1)
    assert s.ai_hand == [c]


def test_ai_recycle_noop_when_discard_empty() -> None:
    s = MatchState(ai_deck=[], ai_discard=[], _rng=random.Random(0))
    s._recycle_ai_discard()
    assert s.ai_deck == []


def test_recycle_and_draw() -> None:
    c = MatchCard("c", "C", 0, 1, 1, 0)
    s = MatchState(
        player_deck=[],
        player_hand=[],
        player_discard=[c],
        _rng=random.Random(0),
    )
    s._recycle_player_discard()
    assert s.player_deck == [c]
    s._draw_player_to(1)
    assert s.player_hand == [c]


def test_simulated_match_ends() -> None:
    pd, ad = mirror_decks()
    s = MatchState.from_decks(pd, ad, rng=random.Random(42), starting_health=12)
    rng = random.Random(7)
    for _ in range(200):
        if s.outcome() != MatchOutcome.ONGOING:
            break
        if not s.player_hand or not s.ai_hand:
            break
        s.play_round(rng.randrange(len(s.player_hand)), rng.randrange(len(s.ai_hand)))
    assert s.outcome() != MatchOutcome.ONGOING
