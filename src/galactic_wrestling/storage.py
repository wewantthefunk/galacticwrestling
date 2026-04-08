from __future__ import annotations

import json
import uuid
from pathlib import Path

from galactic_wrestling.config import data_dir
from galactic_wrestling.models import Alignment, Archetype, Wrestler, utc_now_iso

MAX_WRESTLERS = 5


def _wrestlers_dir(player_id: str) -> Path:
    return data_dir() / "players" / player_id / "wrestlers"


def list_wrestlers(player_id: str) -> list[Wrestler]:
    d = _wrestlers_dir(player_id)
    if not d.is_dir():
        return []
    out: list[Wrestler] = []
    for path in sorted(d.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        out.append(Wrestler.from_json(data))
    out.sort(key=lambda w: w.name.lower())
    return out


def count_wrestlers(player_id: str) -> int:
    d = _wrestlers_dir(player_id)
    if not d.is_dir():
        return 0
    return sum(1 for _ in d.glob("*.json"))


def save_new_wrestler(
    player_id: str,
    name: str,
    archetype: Archetype,
    alignment: Alignment,
    gimmick_id: str,
) -> Wrestler:
    if count_wrestlers(player_id) >= MAX_WRESTLERS:
        raise ValueError(f"You can only have {MAX_WRESTLERS} wrestlers.")
    n = name.strip()
    if not n:
        raise ValueError("Wrestler name cannot be empty.")
    if len(n) > 64:
        raise ValueError("Wrestler name is too long (max 64 characters).")
    wid = str(uuid.uuid4())
    now = utc_now_iso()
    w = Wrestler(
        id=wid,
        name=n,
        archetype=archetype,
        alignment=alignment,
        gimmick_id=gimmick_id,
        created_at=now,
        updated_at=now,
    )
    d = _wrestlers_dir(player_id)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{wid}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(w.to_json(), f, indent=2)
        f.write("\n")
    return w


def delete_wrestler(player_id: str, wrestler_id: str) -> None:
    path = _wrestlers_dir(player_id) / f"{wrestler_id}.json"
    if path.is_file():
        path.unlink()


def rename_wrestler(player_id: str, wrestler_id: str, new_name: str) -> Wrestler:
    n = new_name.strip()
    if not n:
        raise ValueError("Wrestler name cannot be empty.")
    if len(n) > 64:
        raise ValueError("Wrestler name is too long (max 64 characters).")
    path = _wrestlers_dir(player_id) / f"{wrestler_id}.json"
    if not path.is_file():
        raise ValueError("Wrestler not found.")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    w = Wrestler.from_json(data)
    if w.id != wrestler_id:
        raise ValueError("Wrestler id mismatch.")
    w = Wrestler(
        id=w.id,
        name=n,
        archetype=w.archetype,
        alignment=w.alignment,
        gimmick_id=w.gimmick_id,
        created_at=w.created_at,
        updated_at=utc_now_iso(),
    )
    with path.open("w", encoding="utf-8") as f:
        json.dump(w.to_json(), f, indent=2)
        f.write("\n")
    return w
