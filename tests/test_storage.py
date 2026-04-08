from __future__ import annotations

import json
from pathlib import Path

import pytest

from galactic_wrestling import storage
from galactic_wrestling import auth
from galactic_wrestling.models import Alignment, Archetype


def _account(isolated_data_dir: Path):
    return auth.signup("Player", "pw")


def test_save_list_rename_delete(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    w = storage.save_new_wrestler(
        a.player_id, "Z-Man", Archetype.REGULAR, Alignment.BABYFACE, "showman"
    )
    lst = storage.list_wrestlers(a.player_id)
    assert len(lst) == 1
    assert lst[0].name == "Z-Man"
    w2 = storage.rename_wrestler(a.player_id, w.id, "Zed")
    assert w2.name == "Zed"
    storage.delete_wrestler(a.player_id, w.id)
    assert storage.list_wrestlers(a.player_id) == []


def test_list_sorted_by_name(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    storage.save_new_wrestler(a.player_id, "B", Archetype.REGULAR, Alignment.HEEL, "underdog")
    storage.save_new_wrestler(a.player_id, "a", Archetype.REGULAR, Alignment.HEEL, "underdog")
    names = [w.name for w in storage.list_wrestlers(a.player_id)]
    assert names == ["a", "B"]


def test_max_wrestlers(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    for i in range(storage.MAX_WRESTLERS):
        storage.save_new_wrestler(
            a.player_id, f"W{i}", Archetype.REGULAR, Alignment.BABYFACE, "patriot"
        )
    with pytest.raises(ValueError, match="5"):
        storage.save_new_wrestler(
            a.player_id, "Extra", Archetype.REGULAR, Alignment.BABYFACE, "patriot"
        )


def test_save_empty_name(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    with pytest.raises(ValueError, match="empty"):
        storage.save_new_wrestler(a.player_id, "  ", Archetype.REGULAR, Alignment.BABYFACE, "patriot")


def test_rename_empty_name(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    w = storage.save_new_wrestler(
        a.player_id, "A", Archetype.REGULAR, Alignment.BABYFACE, "patriot"
    )
    with pytest.raises(ValueError, match="empty"):
        storage.rename_wrestler(a.player_id, w.id, "   ")


def test_rename_not_found(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    with pytest.raises(ValueError, match="not found"):
        storage.rename_wrestler(a.player_id, "not-a-uuid", "X")


def test_rename_id_mismatch(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    w = storage.save_new_wrestler(
        a.player_id, "A", Archetype.REGULAR, Alignment.BABYFACE, "patriot"
    )
    path = storage._wrestlers_dir(a.player_id) / f"{w.id}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["id"] = "other-id"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="mismatch"):
        storage.rename_wrestler(a.player_id, w.id, "B")


def test_count_and_list_empty_dir(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    d = storage._wrestlers_dir(a.player_id)
    assert storage.count_wrestlers(a.player_id) == 0
    assert storage.list_wrestlers(a.player_id) == []
    d.mkdir(parents=True, exist_ok=True)
    assert storage.count_wrestlers(a.player_id) == 0


def test_list_and_count_when_wrestlers_dir_missing(isolated_data_dir: Path) -> None:
    import shutil

    a = _account(isolated_data_dir)
    shutil.rmtree(storage._wrestlers_dir(a.player_id))
    assert storage.list_wrestlers(a.player_id) == []
    assert storage.count_wrestlers(a.player_id) == 0


def test_save_name_too_long(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    with pytest.raises(ValueError, match="too long"):
        storage.save_new_wrestler(
            a.player_id, "x" * 65, Archetype.REGULAR, Alignment.BABYFACE, "patriot"
        )


def test_rename_name_too_long(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    w = storage.save_new_wrestler(
        a.player_id, "A", Archetype.REGULAR, Alignment.BABYFACE, "patriot"
    )
    with pytest.raises(ValueError, match="too long"):
        storage.rename_wrestler(a.player_id, w.id, "y" * 65)


def test_delete_missing_file_no_error(isolated_data_dir: Path) -> None:
    a = _account(isolated_data_dir)
    storage.delete_wrestler(a.player_id, "00000000-0000-0000-0000-000000000000")
