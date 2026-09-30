from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UpgradeEffects:
    yield_bonus: int = 0


@dataclass(frozen=True)
class StarterUpgrade:
    key: str
    name: str
    description: str
    cash_cost: int
    max_level: int
    effects: UpgradeEffects


@dataclass(frozen=True)
class UpgradesCatalog:
    version: str
    upgrades: tuple[StarterUpgrade, ...]


CATALOG_PATH = Path(__file__).with_name("starter_upgrades.json")


def _require_text(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Upgrade field {field!r} must be a non-empty string.")
    return value.strip()


def _require_positive_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Upgrade field {field!r} must be a positive integer.")
    return value


def _effects(raw: dict[str, Any]) -> UpgradeEffects:
    effects = raw.get("effects")
    if not isinstance(effects, dict):
        raise TypeError("Upgrade effects must be an object.")
    yield_bonus = effects.get("yield_bonus", 0)
    if not isinstance(yield_bonus, int) or yield_bonus < 0:
        raise ValueError("Upgrade yield_bonus must be a non-negative integer.")
    return UpgradeEffects(yield_bonus=yield_bonus)


def load_upgrades_catalog(path: Path = CATALOG_PATH) -> UpgradesCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Upgrades catalog requires a non-empty version.")

    raw_upgrades = payload.get("upgrades")
    if not isinstance(raw_upgrades, list) or not raw_upgrades:
        raise ValueError("Upgrades catalog requires at least one upgrade.")

    seen: set[str] = set()
    upgrades: list[StarterUpgrade] = []
    for raw in raw_upgrades:
        if not isinstance(raw, dict):
            raise TypeError("Every upgrade entry must be an object.")
        key = _require_text(raw, "key")
        if key in seen:
            raise ValueError(f"Duplicate upgrade key: {key}")
        seen.add(key)
        upgrades.append(
            StarterUpgrade(
                key=key,
                name=_require_text(raw, "name"),
                description=_require_text(raw, "description"),
                cash_cost=_require_positive_int(raw, "cash_cost"),
                max_level=_require_positive_int(raw, "max_level"),
                effects=_effects(raw),
            )
        )

    return UpgradesCatalog(version=version.strip(), upgrades=tuple(upgrades))


STARTER_UPGRADES_CATALOG = load_upgrades_catalog()
STARTER_UPGRADES = STARTER_UPGRADES_CATALOG.upgrades
STARTER_UPGRADE_BY_KEY = {upgrade.key: upgrade for upgrade in STARTER_UPGRADES}
