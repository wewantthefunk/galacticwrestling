"""Head-to-head match simulation (two-lane clash, health, decks)."""

from galactic_wrestling.match.engine import MatchState, clash_damage
from galactic_wrestling.match.model import MatchCard, MatchOutcome, RoundResult

__all__ = [
    "MatchCard",
    "MatchOutcome",
    "MatchState",
    "RoundResult",
    "clash_damage",
]
