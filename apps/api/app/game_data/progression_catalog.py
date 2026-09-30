from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProgressionLevel:
    level: int
    xp_required: int
    skill_points_total: int
    unlock: str


@dataclass(frozen=True)
class ProgressionCatalog:
    version: str
    levels: tuple[ProgressionLevel, ...]


CATALOG_PATH = Path(__file__).with_name("progression_levels.json")


def _require_non_negative_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Progression field {field!r} must be a non-negative integer.")
    return value


def _require_text(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Progression field {field!r} must be a non-empty string.")
    return value.strip()


def load_progression_catalog(path: Path = CATALOG_PATH) -> ProgressionCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Progression catalog requires a non-empty version.")

    raw_levels = payload.get("levels")
    if not isinstance(raw_levels, list) or len(raw_levels) < 20:
        raise ValueError("Progression catalog requires at least 20 levels.")

    levels: list[ProgressionLevel] = []
    previous_xp = -1
    previous_points = -1
    for expected_level, raw in enumerate(raw_levels, start=1):
        if not isinstance(raw, dict):
            raise TypeError("Every progression level must be an object.")
        level = _require_non_negative_int(raw, "level")
        xp_required = _require_non_negative_int(raw, "xp_required")
        skill_points_total = _require_non_negative_int(raw, "skill_points_total")
        if level != expected_level:
            raise ValueError("Progression levels must be contiguous starting at 1.")
        if xp_required <= previous_xp:
            raise ValueError("Progression XP requirements must strictly increase.")
        if skill_points_total < previous_points:
            raise ValueError("Progression skill points cannot decrease.")
        previous_xp = xp_required
        previous_points = skill_points_total
        levels.append(
            ProgressionLevel(
                level=level,
                xp_required=xp_required,
                skill_points_total=skill_points_total,
                unlock=_require_text(raw, "unlock"),
            )
        )

    return ProgressionCatalog(version=version.strip(), levels=tuple(levels))


PROGRESSION_CATALOG = load_progression_catalog()
PROGRESSION_LEVELS = PROGRESSION_CATALOG.levels
PROGRESSION_BY_LEVEL = {level.level: level for level in PROGRESSION_LEVELS}
MAX_LEVEL = PROGRESSION_LEVELS[-1].level
