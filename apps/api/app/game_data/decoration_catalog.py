from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any

DECORATION_CONFIG_VERSION = "decorations_v1"


@dataclass(frozen=True)
class DecorationDefinition:
    key: str
    name: str
    category: str
    cost_cash: int
    min_level: int


def load_decorations() -> tuple[DecorationDefinition, ...]:
    raw = resources.files("app.game_data").joinpath("decorations.json").read_text()
    data: dict[str, Any] = json.loads(raw)
    if data.get("version") != DECORATION_CONFIG_VERSION:
        raise ValueError("Decoration catalog version mismatch.")
    records = data.get("items")
    if not isinstance(records, list) or not 40 <= len(records) <= 60:
        raise ValueError("Alpha decoration catalog must define 40-60 items.")

    definitions = tuple(DecorationDefinition(**record) for record in records)
    if len({item.key for item in definitions}) != len(definitions):
        raise ValueError("Decoration keys must be unique.")
    if any(item.cost_cash <= 0 or item.min_level <= 0 for item in definitions):
        raise ValueError("Decoration cost and level must be positive.")
    return definitions


DECORATIONS = load_decorations()
DECORATION_BY_KEY = {item.key: item for item in DECORATIONS}
