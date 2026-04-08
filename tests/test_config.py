from __future__ import annotations

import os
from pathlib import Path

import pytest

from galactic_wrestling.config import data_dir, ensure_data_tree


def test_data_dir_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GALACTIC_WRESTLING_DATA_DIR", raising=False)
    home = Path("/tmp/fakehome")
    monkeypatch.setenv("HOME", str(home))
    d = data_dir()
    assert d == (home / ".galactic-wrestling").resolve()


def test_data_dir_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GALACTIC_WRESTLING_DATA_DIR", str(tmp_path / "x"))
    assert data_dir() == (tmp_path / "x").resolve()


def test_ensure_data_tree_creates_players(isolated_data_dir: Path) -> None:
    root = ensure_data_tree()
    assert root.is_dir()
    assert (root / "players").is_dir()
