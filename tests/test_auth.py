from __future__ import annotations

import json
from pathlib import Path

import pytest

from galactic_wrestling import auth
from galactic_wrestling.config import data_dir, ensure_data_tree


def test_signup_and_login(isolated_data_dir: Path) -> None:
    a = auth.signup("Alice", "secret12")
    assert a.login_name == "Alice"
    b = auth.login("alice", "secret12")
    assert b.player_id == a.player_id
    assert b.login_name == "Alice"


def test_signup_case_insensitive_duplicate(isolated_data_dir: Path) -> None:
    auth.signup("Bob", "pw")
    with pytest.raises(ValueError, match="already taken"):
        auth.signup("bob", "other")


def test_signup_empty_name(isolated_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        auth.signup("   ", "pw")


def test_signup_name_too_long(isolated_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="too long"):
        auth.signup("x" * 65, "pw")


def test_login_empty_name(isolated_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        auth.login("  ", "pw")


def test_login_unknown_user(isolated_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="Unknown"):
        auth.login("nobody", "pw")


def test_login_wrong_password(isolated_data_dir: Path) -> None:
    auth.signup("Carol", "rightpw")
    with pytest.raises(ValueError, match="Unknown"):
        auth.login("Carol", "wrongpw")


def test_login_missing_account_file(isolated_data_dir: Path) -> None:
    a = auth.signup("Dan", "pw")
    acc = auth._account_path(a.player_id)
    acc.unlink()
    with pytest.raises(ValueError, match="missing"):
        auth.login("Dan", "pw")


def test_registry_missing_accounts_key_merged(isolated_data_dir: Path) -> None:
    ensure_data_tree()
    reg = data_dir() / "registry.json"
    reg.write_text(json.dumps({"version": 1}))
    with pytest.raises(ValueError):
        auth.login("x", "y")


def test_login_display_name_fallback(isolated_data_dir: Path) -> None:
    a = auth.signup("Eve", "pw")
    path = auth._account_path(a.player_id)
    doc = json.loads(path.read_text(encoding="utf-8"))
    del doc["login_name"]
    path.write_text(json.dumps(doc), encoding="utf-8")
    b = auth.login("Eve", "pw")
    assert b.login_name == "Eve"
