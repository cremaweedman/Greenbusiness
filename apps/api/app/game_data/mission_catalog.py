from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import date
from importlib import resources
from typing import Any

MISSION_CONFIG_VERSION = "missions_v2"
MASTERY_THRESHOLDS = (10, 25, 50)


@dataclass(frozen=True)
class ContactDefinition:
    key: str
    name: str
    role: str
    tone: str
    intro_message: str


@dataclass(frozen=True)
class MissionDefinition:
    key: str
    sequence: int
    contact_key: str
    arc_key: str
    arc_title: str
    title: str
    description: str
    objective_type: str
    objective_key: str | None
    target: int
    reward_cash: int
    reward_xp: int
    reward_reputation: int
    daily_eligible: bool
    weekly_eligible: bool
    inbox_message: str


def _load_json(name: str) -> dict[str, Any]:
    raw = resources.files("app.game_data").joinpath(name).read_text()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("version") != MISSION_CONFIG_VERSION:
        raise ValueError(f"{name} must use {MISSION_CONFIG_VERSION}.")
    return data


def load_contacts() -> tuple[ContactDefinition, ...]:
    data = _load_json("contacts.json")
    records = data.get("contacts")
    if not isinstance(records, list) or not 3 <= len(records) <= 6:
        raise ValueError("contacts.json must define 3-6 original contacts.")
    contacts = tuple(ContactDefinition(**record) for record in records)
    if len({item.key for item in contacts}) != len(contacts):
        raise ValueError("Contact keys must be unique.")
    return contacts


def load_missions() -> tuple[MissionDefinition, ...]:
    data = _load_json("starter_missions.json")
    records = data.get("missions")
    if not isinstance(records, list) or not 25 <= len(records) <= 40:
        raise ValueError("starter_missions.json must define 25-40 missions.")
    missions = tuple(MissionDefinition(**record) for record in records)
    if len({item.key for item in missions}) != len(missions):
        raise ValueError("Mission keys must be unique.")
    if [item.sequence for item in missions] != list(range(1, len(missions) + 1)):
        raise ValueError("Mission sequence must be contiguous and start at 1.")
    supported = {"plant", "care", "harvest", "contract_complete", "cash_earned", "upgrade_owned"}
    if any(item.objective_type not in supported for item in missions):
        raise ValueError("Mission objective type is unsupported.")
    if any(item.target <= 0 for item in missions):
        raise ValueError("Mission target must be positive.")
    contact_keys = {item.key for item in CONTACTS}
    if any(item.contact_key not in contact_keys for item in missions):
        raise ValueError("Every mission contact_key must exist in contacts.json.")
    if len({item.arc_key for item in missions}) < 3:
        raise ValueError("Mission library must contain at least 3 narrative arcs.")
    return missions


CONTACTS = load_contacts()
CONTACT_BY_KEY = {item.key: item for item in CONTACTS}
MISSIONS = load_missions()
MISSION_BY_KEY = {item.key: item for item in MISSIONS}


def cosmetic_keys_for_variety(variety_key: str, points: int) -> list[str]:
    rewards: list[str] = []
    if points >= 10:
        rewards.append(f"cosmetic.variety.{variety_key}.accent-badge")
    if points >= 25:
        rewards.append(f"cosmetic.variety.{variety_key}.signature-label")
    if points >= 50:
        rewards.append(f"cosmetic.variety.{variety_key}.showcase-planter")
    return rewards


def cosmetic_key_for_variety(variety_key: str) -> str:
    return f"cosmetic.variety.{variety_key}.signature-label"


def mastery_tier(points: int) -> int:
    return sum(points >= threshold for threshold in MASTERY_THRESHOLDS)


def next_mastery_threshold(points: int) -> int | None:
    return next((threshold for threshold in MASTERY_THRESHOLDS if points < threshold), None)


def deterministic_pool(
    *,
    user_id: uuid.UUID,
    period_key: str,
    eligible_keys: list[str],
    count: int,
) -> list[str]:
    ranked = sorted(
        eligible_keys,
        key=lambda key: hashlib.sha256(
            f"{MISSION_CONFIG_VERSION}:{user_id}:{period_key}:{key}".encode()
        ).hexdigest(),
    )
    return ranked[:count]


def daily_period_key(day: date) -> str:
    return day.isoformat()


def weekly_period_key(day: date) -> str:
    iso_year, iso_week, _ = day.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def daily_pool_keys(user_id: uuid.UUID, day: date) -> list[str]:
    eligible = [item.key for item in MISSIONS if item.daily_eligible]
    return deterministic_pool(
        user_id=user_id,
        period_key=f"day:{daily_period_key(day)}",
        eligible_keys=eligible,
        count=min(2, len(eligible)),
    )


def weekly_pool_keys(user_id: uuid.UUID, day: date) -> list[str]:
    eligible = [item.key for item in MISSIONS if item.weekly_eligible]
    return deterministic_pool(
        user_id=user_id,
        period_key=f"week:{weekly_period_key(day)}",
        eligible_keys=eligible,
        count=min(3, len(eligible)),
    )
