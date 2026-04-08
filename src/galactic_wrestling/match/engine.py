from __future__ import annotations

import random
from dataclasses import dataclass, field

from galactic_wrestling.match.model import MatchCard, MatchOutcome, RoundResult

DEFAULT_STARTING_HEALTH = 30
HAND_SIZE = 5


def clash_damage(player_card: MatchCard, ai_card: MatchCard) -> tuple[int, int]:
    """Two-lane resolution: player offense vs AI defense; AI offense vs player defense.

    Returns ``(damage_to_player, damage_to_ai)`` using strict ``>`` on each lane.
    Damage on a winning lane is ``attacker_offense - defender_defense`` (positive integer).
    """
    dmg_to_ai = 0
    if player_card.offense > ai_card.defense:
        dmg_to_ai = player_card.offense - ai_card.defense
    dmg_to_player = 0
    if ai_card.offense > player_card.defense:
        dmg_to_player = ai_card.offense - player_card.defense
    return dmg_to_player, dmg_to_ai


@dataclass
class MatchState:
    """In-memory match: two decks, hands, health, simultaneous play per round."""

    player_deck: list[MatchCard] = field(default_factory=list)
    ai_deck: list[MatchCard] = field(default_factory=list)
    player_hand: list[MatchCard] = field(default_factory=list)
    ai_hand: list[MatchCard] = field(default_factory=list)
    player_discard: list[MatchCard] = field(default_factory=list)
    ai_discard: list[MatchCard] = field(default_factory=list)
    player_health: int = DEFAULT_STARTING_HEALTH
    ai_health: int = DEFAULT_STARTING_HEALTH
    starting_health: int = DEFAULT_STARTING_HEALTH
    _rng: random.Random = field(default_factory=random.Random)

    @classmethod
    def from_decks(
        cls,
        player_deck: list[MatchCard],
        ai_deck: list[MatchCard],
        *,
        starting_health: int = DEFAULT_STARTING_HEALTH,
        rng: random.Random | None = None,
    ) -> MatchState:
        """Build state, shuffle both decks, draw opening hands."""
        rng = rng or random.Random()
        pd = player_deck.copy()
        ad = ai_deck.copy()
        rng.shuffle(pd)
        rng.shuffle(ad)
        s = cls(
            player_deck=pd,
            ai_deck=ad,
            starting_health=starting_health,
            player_health=starting_health,
            ai_health=starting_health,
            _rng=rng,
        )
        s._draw_player_to(HAND_SIZE)
        s._draw_ai_to(HAND_SIZE)
        return s

    def outcome(self) -> MatchOutcome:
        if self.player_health <= 0 and self.ai_health <= 0:
            return MatchOutcome.DRAW
        if self.player_health <= 0:
            return MatchOutcome.AI_WINS
        if self.ai_health <= 0:
            return MatchOutcome.PLAYER_WINS
        return MatchOutcome.ONGOING

    def play_round(self, player_hand_index: int, ai_hand_index: int) -> RoundResult:
        """Play one card from each hand; resolve clash; discard; draw to hand size."""
        if self.outcome() != MatchOutcome.ONGOING:
            raise RuntimeError("Match is already over.")
        if not self.player_hand or not self.ai_hand:
            raise RuntimeError("Cannot play: empty hand.")
        if player_hand_index < 0 or player_hand_index >= len(self.player_hand):
            raise ValueError("Invalid player hand index.")
        if ai_hand_index < 0 or ai_hand_index >= len(self.ai_hand):
            raise ValueError("Invalid AI hand index.")

        pc = self.player_hand.pop(player_hand_index)
        ac = self.ai_hand.pop(ai_hand_index)

        dmg_p, dmg_a = clash_damage(pc, ac)
        self.player_health = max(0, self.player_health - dmg_p)
        self.ai_health = max(0, self.ai_health - dmg_a)

        self.player_discard.append(pc)
        self.ai_discard.append(ac)

        self._draw_player_to(HAND_SIZE)
        self._draw_ai_to(HAND_SIZE)

        return RoundResult(
            player_card=pc,
            ai_card=ac,
            damage_to_player=dmg_p,
            damage_to_ai=dmg_a,
            player_health_after=self.player_health,
            ai_health_after=self.ai_health,
        )

    def _draw_player_to(self, target: int) -> None:
        while len(self.player_hand) < target:
            if not self.player_deck:
                self._recycle_player_discard()
            if not self.player_deck:
                break
            self.player_hand.append(self.player_deck.pop())

    def _draw_ai_to(self, target: int) -> None:
        while len(self.ai_hand) < target:
            if not self.ai_deck:
                self._recycle_ai_discard()
            if not self.ai_deck:
                break
            self.ai_hand.append(self.ai_deck.pop())

    def _recycle_player_discard(self) -> None:
        if not self.player_discard:
            return
        self.player_deck.extend(self.player_discard)
        self.player_discard.clear()
        self._rng.shuffle(self.player_deck)

    def _recycle_ai_discard(self) -> None:
        if not self.ai_discard:
            return
        self.ai_deck.extend(self.ai_discard)
        self.ai_discard.clear()
        self._rng.shuffle(self.ai_deck)
