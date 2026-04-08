from __future__ import annotations

from galactic_wrestling.gimmicks import GIMMICKS, gimmick_by_id, is_valid_gimmick_id


def test_gimmick_ids_unique() -> None:
    ids = [g.id for g in GIMMICKS]
    assert len(ids) == len(set(ids))


def test_gimmick_by_id_found() -> None:
    g = gimmick_by_id("patriot")
    assert g is not None
    assert g.name


def test_gimmick_by_id_missing() -> None:
    assert gimmick_by_id("no_such_id") is None


def test_is_valid_gimmick_id() -> None:
    assert is_valid_gimmick_id("underdog") is True
    assert is_valid_gimmick_id("nope") is False
