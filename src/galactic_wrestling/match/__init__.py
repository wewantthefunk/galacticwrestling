"""Head-to-head match simulation (two-lane clash, health, decks)."""

from galactic_wrestling.match.ai_policy import choose_ai_hand_index
from galactic_wrestling.match.deck_builder import build_match_decks, card_value
from galactic_wrestling.match.engine import MatchState, clash_damage
from galactic_wrestling.match.model import MatchCard, MatchOutcome, RoundResult

__all__ = [
    "MatchCard",
    "MatchOutcome",
    "MatchState",
    "RoundResult",
    "build_match_decks",
    "card_value",
    "choose_ai_hand_index",
    "clash_damage",
]
