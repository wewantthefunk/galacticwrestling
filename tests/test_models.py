from __future__ import annotations

import pytest

from galactic_wrestling.models import (
    Alignment,
    Archetype,
    Wrestler,
    normalize_login_key,
    utc_now_iso,
)


def test_normalize_login_key() -> None:
    assert normalize_login_key("  Alice  ") == "alice"


def test_utc_now_iso_format() -> None:
    s = utc_now_iso()
    assert "T" in s
    assert s.endswith("+00:00")


def test_wrestler_roundtrip_json() -> None:
    w = Wrestler(
        id="wid",
        name="Test",
        archetype=Archetype.FLYER,
        alignment=Alignment.HEEL,
        gimmick_id="patriot",
        created_at="2020-01-01T00:00:00+00:00",
        updated_at="2020-01-02T00:00:00+00:00",
    )
    data = w.to_json()
    w2 = Wrestler.from_json(data)
    assert w2 == w


def test_wrestler_from_json_strings() -> None:
    w = Wrestler.from_json(
        {
            "id": 1,
            "name": "X",
            "archetype": "Giant",
            "alignment": "Babyface",
            "gimmick_id": "monster",
            "created_at": "t1",
            "updated_at": "t2",
        }
    )
    assert w.id == "1"
    assert w.archetype == Archetype.GIANT


def test_invalid_archetype_raises() -> None:
    with pytest.raises(ValueError):
        Wrestler.from_json(
            {
                "id": "a",
                "name": "n",
                "archetype": "NotAnArchetype",
                "alignment": "Babyface",
                "gimmick_id": "x",
                "created_at": "t",
                "updated_at": "t",
            }
        )
