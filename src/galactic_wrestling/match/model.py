from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MatchOutcome(StrEnum):
    ONGOING = "ongoing"
    PLAYER_WINS = "player_wins"
    AI_WINS = "ai_wins"
    DRAW = "draw"


@dataclass(frozen=True)
class MatchCard:
    """Runtime card for match resolution (numeric attributes)."""

    id: str
    name: str
    cost: int
    offense: int
    defense: int
    heat: int
    special: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "offense": self.offense,
            "defense": self.defense,
            "heat": self.heat,
            "special": self.special,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> MatchCard:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            cost=int(data["cost"]),
            offense=int(data["offense"]),
            defense=int(data["defense"]),
            heat=int(data["heat"]),
            special=(
                None if data.get("special") in (None, "") else str(data["special"])
            ),
        )


@dataclass(frozen=True)
class RoundResult:
    player_card: MatchCard
    ai_card: MatchCard
    damage_to_player: int
    damage_to_ai: int
    player_health_after: int
    ai_health_after: int
