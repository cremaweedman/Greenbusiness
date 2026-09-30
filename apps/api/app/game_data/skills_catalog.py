from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillEffects:
    care_yield_bonus: int = 0
    contract_cash_bonus: int = 0
    grow_seconds_reduction: int = 0


@dataclass(frozen=True)
class SkillNode:
    key: str
    branch: str
    name: str
    description: str
    max_rank: int
    cost_per_rank: int
    effects: SkillEffects


@dataclass(frozen=True)
class SkillsCatalog:
    version: str
    skills: tuple[SkillNode, ...]


SKILL_BRANCHES = {"botany", "commerce", "operations"}
CATALOG_PATH = Path(__file__).with_name("skill_trees.json")


def _require_text(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Skill field {field!r} must be a non-empty string.")
    return value.strip()


def _require_positive_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Skill field {field!r} must be a positive integer.")
    return value


def _require_non_negative_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Skill field {field!r} must be a non-negative integer.")
    return value


def _effects(raw: dict[str, Any]) -> SkillEffects:
    effects = raw.get("effects")
    if not isinstance(effects, dict):
        raise TypeError("Skill effects must be an object.")
    return SkillEffects(
        care_yield_bonus=_require_non_negative_int(effects, "care_yield_bonus"),
        contract_cash_bonus=_require_non_negative_int(effects, "contract_cash_bonus"),
        grow_seconds_reduction=_require_non_negative_int(effects, "grow_seconds_reduction"),
    )


def load_skills_catalog(path: Path = CATALOG_PATH) -> SkillsCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Skills catalog requires a non-empty version.")

    raw_skills = payload.get("skills")
    if not isinstance(raw_skills, list) or len(raw_skills) < 3:
        raise ValueError("Skills catalog requires at least one skill per starter branch.")

    seen: set[str] = set()
    skills: list[SkillNode] = []
    for raw in raw_skills:
        if not isinstance(raw, dict):
            raise TypeError("Every skill entry must be an object.")
        key = _require_text(raw, "key")
        if key in seen:
            raise ValueError(f"Duplicate skill key: {key}")
        seen.add(key)

        branch = _require_text(raw, "branch")
        if branch not in SKILL_BRANCHES:
            raise ValueError(f"Unsupported skill branch: {branch}")

        skills.append(
            SkillNode(
                key=key,
                branch=branch,
                name=_require_text(raw, "name"),
                description=_require_text(raw, "description"),
                max_rank=_require_positive_int(raw, "max_rank"),
                cost_per_rank=_require_positive_int(raw, "cost_per_rank"),
                effects=_effects(raw),
            )
        )

    branches = {skill.branch for skill in skills}
    if branches != SKILL_BRANCHES:
        raise ValueError("Skills catalog must cover botany, commerce and operations.")

    return SkillsCatalog(version=version.strip(), skills=tuple(skills))


SKILLS_CATALOG = load_skills_catalog()
SKILLS = SKILLS_CATALOG.skills
SKILL_BY_KEY = {skill.key: skill for skill in SKILLS}
