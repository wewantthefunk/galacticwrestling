from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class Archetype(StrEnum):
    GIANT = "Giant"
    FLYER = "Flyer"
    JOBBER = "Jobber"
    FLASHY = "Flashy"
    COMEDY = "Comedy"
    REGULAR = "Regular"


class Alignment(StrEnum):
    BABYFACE = "Babyface"
    HEEL = "Heel"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Wrestler:
    id: str
    name: str
    archetype: Archetype
    alignment: Alignment
    gimmick_id: str
    created_at: str
    updated_at: str

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "archetype": self.archetype.value,
            "alignment": self.alignment.value,
            "gimmick_id": self.gimmick_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Wrestler:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            archetype=Archetype(str(data["archetype"])),
            alignment=Alignment(str(data["alignment"])),
            gimmick_id=str(data["gimmick_id"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )


def normalize_login_key(name: str) -> str:
    return name.strip().lower()
