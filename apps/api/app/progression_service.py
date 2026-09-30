from __future__ import annotations

from typing import TYPE_CHECKING

from app.game_data.progression_catalog import MAX_LEVEL, PROGRESSION_BY_LEVEL, PROGRESSION_LEVELS
from app.schemas import ProgressionResponse

if TYPE_CHECKING:
    from app.db.models import Progression


def level_for_xp(xp: int) -> int:
    current_level = 1
    for level in PROGRESSION_LEVELS:
        if xp >= level.xp_required:
            current_level = level.level
        else:
            break
    return current_level


def apply_xp(progression: Progression, xp_delta: int) -> int:
    previous_level = progression.level
    progression.xp += xp_delta
    next_level = level_for_xp(progression.xp)
    if next_level > previous_level:
        previous_points = PROGRESSION_BY_LEVEL[previous_level].skill_points_total
        next_points = PROGRESSION_BY_LEVEL[next_level].skill_points_total
        progression.skill_points += next_points - previous_points
        progression.level = next_level
    return progression.level - previous_level


def progression_response(progression: Progression) -> ProgressionResponse:
    current = PROGRESSION_BY_LEVEL[progression.level]
    next_level = PROGRESSION_BY_LEVEL.get(progression.level + 1)
    return ProgressionResponse(
        level=progression.level,
        xp=progression.xp,
        reputation=progression.reputation,
        skill_points=progression.skill_points,
        max_level=MAX_LEVEL,
        current_level_xp=current.xp_required,
        next_level_xp=next_level.xp_required if next_level is not None else None,
        next_unlock=next_level.unlock if next_level is not None else None,
    )
