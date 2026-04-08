from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    """Root directory for saves (registry, player folders)."""
    raw = os.environ.get("GALACTIC_WRESTLING_DATA_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.home() / ".galactic-wrestling").resolve()


def ensure_data_tree() -> Path:
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    (root / "players").mkdir(exist_ok=True)
    return root
