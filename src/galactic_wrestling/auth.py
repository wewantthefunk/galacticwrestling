from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from galactic_wrestling.config import data_dir, ensure_data_tree
from galactic_wrestling.models import normalize_login_key, utc_now_iso

_HASHER = PasswordHasher()


@dataclass(frozen=True)
class Account:
    player_id: str
    login_name: str


def _registry_path() -> Path:
    return data_dir() / "registry.json"


def _account_path(player_id: str) -> Path:
    return data_dir() / "players" / player_id / "account.json"


def _load_registry() -> dict[str, Any]:
    path = _registry_path()
    if not path.is_file():
        return {"version": 1, "accounts": {}}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if "accounts" not in data:
        data["accounts"] = {}
    return data


def _save_registry(data: dict[str, Any]) -> None:
    ensure_data_tree()
    path = _registry_path()
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    tmp.replace(path)


def signup(login_name: str, password: str) -> Account:
    """Create a new account. Raises ValueError on duplicate or invalid input."""
    name = login_name.strip()
    if not name:
        raise ValueError("Login name cannot be empty.")
    if len(name) > 64:
        raise ValueError("Login name is too long (max 64 characters).")
    key = normalize_login_key(name)
    ensure_data_tree()
    reg = _load_registry()
    if key in reg["accounts"]:
        raise ValueError("That login name is already taken.")
    player_id = str(uuid.uuid4())
    pw_hash = _HASHER.hash(password)
    player_root = data_dir() / "players" / player_id
    wrestlers_dir = player_root / "wrestlers"
    wrestlers_dir.mkdir(parents=True, exist_ok=True)
    now = utc_now_iso()
    account_doc = {
        "player_id": player_id,
        "login_name": name,
        "created_at": now,
        "password_hash": pw_hash,
    }
    acc_path = _account_path(player_id)
    with acc_path.open("w", encoding="utf-8") as f:
        json.dump(account_doc, f, indent=2)
        f.write("\n")
    reg["accounts"][key] = {"player_id": player_id}
    _save_registry(reg)
    return Account(player_id=player_id, login_name=name)


def login(login_name: str, password: str) -> Account:
    """Verify credentials. Raises ValueError on failure."""
    name = login_name.strip()
    if not name:
        raise ValueError("Login name cannot be empty.")
    key = normalize_login_key(name)
    reg = _load_registry()
    entry = reg["accounts"].get(key)
    if not entry:
        raise ValueError("Unknown login name or wrong password.")
    player_id = entry["player_id"]
    acc_path = _account_path(player_id)
    if not acc_path.is_file():
        raise ValueError("Account data is missing.")
    with acc_path.open(encoding="utf-8") as f:
        doc = json.load(f)
    stored = doc.get("password_hash", "")
    try:
        _HASHER.verify(stored, password)
    except VerifyMismatchError as e:
        raise ValueError("Unknown login name or wrong password.") from e
    display = str(doc.get("login_name", name))
    return Account(player_id=player_id, login_name=display)
