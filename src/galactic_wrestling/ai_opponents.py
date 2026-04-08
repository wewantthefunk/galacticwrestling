"""AI opponent wrestlers for single-player mode (one per archetype, shared roster)."""

from __future__ import annotations

import json
import random
import uuid
from pathlib import Path

from galactic_wrestling.config import data_dir, ensure_data_tree
from galactic_wrestling.gimmicks import GIMMICKS
from galactic_wrestling.models import Alignment, Archetype, Wrestler, utc_now_iso

# Wrestling-style random name parts (avoid extra dependencies).
HANDLES = (
    "Crimson",
    "Steel",
    "Iron",
    "Neon",
    "Cosmic",
    "Turbo",
    "Voltage",
    "Shadow",
    "Solar",
    "Giga",
    "Nano",
    "Phantom",
    "Quantum",
    "Void",
    "Star",
    "Nova",
    "Astro",
    "Cyber",
    "Rogue",
    "Blitz",
)

NICKS = (
    "Wrecker",
    "Crusher",
    "Viper",
    "Wolf",
    "Bulldog",
    "Comet",
    "Slam",
    "Bomb",
    "Flash",
    "Storm",
    "Panther",
    "Axe",
    "Hammer",
    "Spike",
    "Doom",
    "Rage",
    "Fang",
    "Titan",
    "Spectre",
    "Havoc",
)


def ai_opponents_dir() -> Path:
    return data_dir() / "ai_opponents"


def list_ai_wrestlers() -> list[Wrestler]:
    d = ai_opponents_dir()
    if not d.is_dir():
        return []
    out: list[Wrestler] = []
    for path in sorted(d.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        out.append(Wrestler.from_json(data))
    out.sort(key=lambda w: w.name.lower())
    return out


def _save_ai_wrestler(w: Wrestler) -> None:
    d = ai_opponents_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{w.id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(w.to_json(), f, indent=2)
        f.write("\n")


def _random_name(rng: random.Random, taken: set[str]) -> str:
    for _ in range(100):
        name = f"{rng.choice(HANDLES)} {rng.choice(NICKS)}"
        if name not in taken:
            return name
    name = f"Bot {rng.randint(10_000, 99_999)}"
    if name not in taken:
        return name
    return f"Bot {uuid.uuid4().hex[:8]}"


def _create_ai_wrestler(archetype: Archetype, rng: random.Random, taken_names: set[str]) -> Wrestler:
    name = _random_name(rng, taken_names)
    taken_names.add(name)
    align = rng.choice(list(Alignment))
    gimmick_id = rng.choice(GIMMICKS).id
    wid = str(uuid.uuid4())
    now = utc_now_iso()
    return Wrestler(
        id=wid,
        name=name,
        archetype=archetype,
        alignment=align,
        gimmick_id=gimmick_id,
        created_at=now,
        updated_at=now,
    )


def ensure_ai_opponents(rng: random.Random | None = None) -> list[Wrestler]:
    """Ensure there is one AI wrestler per :class:`Archetype`.

    Creates only missing archetypes. Returns the list of wrestlers **created** this call
    (empty if the roster was already complete).
    """
    ensure_data_tree()
    rng = rng or random.Random()
    existing = list_ai_wrestlers()
    by_arch: dict[Archetype, Wrestler] = {w.archetype: w for w in existing}
    taken_names = {w.name for w in existing}
    created: list[Wrestler] = []
    for arch in Archetype:
        if arch in by_arch:
            continue
        w = _create_ai_wrestler(arch, rng, taken_names)
        _save_ai_wrestler(w)
        created.append(w)
    return created


def _cli() -> None:  # pragma: no cover
    n = len(ensure_ai_opponents())
    print(f"Created {n} new AI opponent(s); roster has {len(list_ai_wrestlers())} total.")


if __name__ == "__main__":  # pragma: no cover
    _cli()
