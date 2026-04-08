from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gimmick:
    id: str
    name: str
    description: str


GIMMICKS: tuple[Gimmick, ...] = (
    Gimmick(
        id="underdog",
        name="Underdog",
        description="Crowd sympathy; comeback bonuses to Heat (later).",
    ),
    Gimmick(
        id="patriot",
        name="Patriot",
        description="Flag imagery; special patriotic finishers.",
    ),
    Gimmick(
        id="monster",
        name="Monster",
        description="Intimidation; destructive signature moves.",
    ),
    Gimmick(
        id="technician",
        name="Technician",
        description="Counters and limb work; technical finishers.",
    ),
    Gimmick(
        id="showman",
        name="Showman",
        description="High drama; flashy Heat spikes.",
    ),
    Gimmick(
        id="rulebreaker",
        name="Rulebreaker",
        description="Cheap shots; illegal shortcuts to Heat.",
    ),
)


def gimmick_by_id(gimmick_id: str) -> Gimmick | None:
    for g in GIMMICKS:
        if g.id == gimmick_id:
            return g
    return None


def is_valid_gimmick_id(gimmick_id: str) -> bool:
    return gimmick_by_id(gimmick_id) is not None
