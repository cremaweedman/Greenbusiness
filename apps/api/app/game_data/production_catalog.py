from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any


@dataclass(frozen=True)
class StarterVariety:
    key: str
    name: str
    grow_seconds: int
    base_yield: int

    @property
    def item_key(self) -> str:
        return f"starter_crop.{self.key}"


def _require_positive_int(value: Any, field: str, key: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Starter variety {key!r} has invalid {field}.")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Starter variety has invalid {field}.")
    return value.strip()


def load_starter_varieties() -> tuple[StarterVariety, ...]:
    raw = resources.files("app.game_data").joinpath("starter_varieties.json").read_text()
    records = json.loads(raw)
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError("Starter variety data must define exactly 3 records.")

    varieties: list[StarterVariety] = []
    seen_keys: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("Starter variety data contains a non-object record.")
        key = _require_string(record.get("key"), "key")
        if key in seen_keys:
            raise ValueError(f"Starter variety key {key!r} is duplicated.")
        seen_keys.add(key)
        varieties.append(
            StarterVariety(
                key=key,
                name=_require_string(record.get("name"), "name"),
                grow_seconds=_require_positive_int(record.get("grow_seconds"), "grow_seconds", key),
                base_yield=_require_positive_int(record.get("base_yield"), "base_yield", key),
            )
        )
    return tuple(varieties)


STARTER_VARIETIES = load_starter_varieties()
STARTER_VARIETY_BY_KEY = {variety.key: variety for variety in STARTER_VARIETIES}
