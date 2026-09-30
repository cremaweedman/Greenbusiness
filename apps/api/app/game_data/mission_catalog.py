from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import date
from importlib import resources
from typing import Any

MISSION_CONFIG_VERSION = "missions_v1"
MASTERY_THRESHOLDS = (10, 25, 50)
MASTERY_COSMETIC_THRESHOLD = 25


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


def _load_json(name: str) -> dict[str, Any]:
    raw = resources.files("app.game_data").joinpath(name).read_text()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("version") != MISSION_CONFIG_VERSION:
        raise ValueError(f"{name} must use {MISSION_CONFIG_VERSION}.")
    return data


def load_contacts() -> tuple[ContactDefinition, ...]:
    data = _load_json("contacts.json")
    records = data.get("contacts")
    if not isinstance(records, list) or len(records) != 2:
        raise ValueError("contacts.json must define exactly 2 contacts.")
    contacts = tuple(ContactDefinition(**record) for record in records)
    if len({item.key for item in contacts}) != len(contacts):
        raise ValueError("Contact keys must be unique.")
    return contacts


def load_missions() -> tuple[MissionDefinition, ...]:
    data = _load_json("starter_missions.json")
    records = data.get("missions")
    if not isinstance(records, list) or not 10 <= len(records) <= 12:
        raise ValueError("starter_missions.json must define 10-12 missions.")
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
    return missions


CONTACTS = load_contacts()
CONTACT_BY_KEY = {item.key: item for item in CONTACTS}
MISSIONS = load_missions()
MISSION_BY_KEY = {item.key: item for item in MISSIONS}


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


def daily_pool_keys(user_id: uuid.UUID, day: date) -> list[str]:
    eligible = [item.key for item in MISSIONS if item.daily_eligible]
    return deterministic_pool(
        user_id=user_id,
        period_key=f"day:{day.isoformat()}",
        eligible_keys=eligible,
        count=min(2, len(eligible)),
    )


def weekly_pool_keys(user_id: uuid.UUID, day: date) -> list[str]:
    iso_year, iso_week, _ = day.isocalendar()
    eligible = [item.key for item in MISSIONS if item.weekly_eligible]
    return deterministic_pool(
        user_id=user_id,
        period_key=f"week:{iso_year}-{iso_week:02d}",
        eligible_keys=eligible,
        count=min(3, len(eligible)),
    )
