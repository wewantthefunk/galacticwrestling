from __future__ import annotations

import random
from pathlib import Path

import pytest

from galactic_wrestling.ai_opponents import ai_opponents_dir, ensure_ai_opponents, list_ai_wrestlers
from galactic_wrestling.models import Archetype


def test_list_empty_when_no_dir(isolated_data_dir: Path) -> None:
    assert list_ai_wrestlers() == []


def test_ensure_creates_six_one_per_archetype(isolated_data_dir: Path) -> None:
    rng = random.Random(42)
    created = ensure_ai_opponents(rng=rng)
    assert len(created) == 6
    roster = list_ai_wrestlers()
    assert len(roster) == 6
    assert {w.archetype for w in roster} == set(Archetype)
    for w in roster:
        assert w.name
        assert w.gimmick_id


def test_ensure_idempotent(isolated_data_dir: Path) -> None:
    ensure_ai_opponents(rng=random.Random(0))
    assert ensure_ai_opponents(rng=random.Random(0)) == []


def test_ensure_fills_missing_file(isolated_data_dir: Path) -> None:
    rng = random.Random(1)
    ensure_ai_opponents(rng=rng)
    roster = list_ai_wrestlers()
    removed = roster[0]
    path = ai_opponents_dir() / f"{removed.id}.json"
    path.unlink()
    assert removed.archetype not in {w.archetype for w in list_ai_wrestlers()}
    added = ensure_ai_opponents(rng=random.Random(2))
    assert len(added) == 1
    assert added[0].archetype == removed.archetype
    assert {w.archetype for w in list_ai_wrestlers()} == set(Archetype)


class _RngBot12345(random.Random):
    def randint(self, a: int, b: int) -> int:
        return 12_345


def test_random_name_bot_number_when_free(monkeypatch: pytest.MonkeyPatch) -> None:
    import galactic_wrestling.ai_opponents as ap

    rng = _RngBot12345(0)
    taken: set[str] = {"A B"}
    monkeypatch.setattr(ap, "HANDLES", ("A",))
    monkeypatch.setattr(ap, "NICKS", ("B",))
    assert ap._random_name(rng, taken) == "Bot 12345"


class _RngBot50000(random.Random):
    def randint(self, a: int, b: int) -> int:
        return 50_000


def test_random_name_uuid_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    import galactic_wrestling.ai_opponents as ap

    rng = _RngBot50000(0)
    taken: set[str] = {"A B", "Bot 50000"}
    monkeypatch.setattr(ap, "HANDLES", ("A",))
    monkeypatch.setattr(ap, "NICKS", ("B",))
    name = ap._random_name(rng, taken)
    assert name.startswith("Bot ")
    assert name != "Bot 50000"
    assert len(name) > 4
