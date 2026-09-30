from __future__ import annotations

from app.game_data.progression_catalog import MAX_LEVEL, PROGRESSION_LEVELS
from app.progression_service import apply_xp, level_for_xp, progression_response


class FakeProgression:
    def __init__(self) -> None:
        self.level = 1
        self.xp = 0
        self.reputation = 0
        self.skill_points = 0


def test_progression_catalog_has_twenty_level_curve():
    assert MAX_LEVEL == 20
    assert len(PROGRESSION_LEVELS) == 20
    assert PROGRESSION_LEVELS[0].xp_required == 0
    assert PROGRESSION_LEVELS[-1].skill_points_total == 20


def test_progression_level_for_xp_uses_server_curve():
    assert level_for_xp(0) == 1
    assert level_for_xp(24) == 1
    assert level_for_xp(25) == 2
    assert level_for_xp(60) == 3


def test_apply_xp_awards_skill_points_only_on_level_up():
    progression = FakeProgression()
    assert apply_xp(progression, 20) == 0
    assert progression.level == 1
    assert progression.skill_points == 0

    assert apply_xp(progression, 40) == 2
    assert progression.level == 3
    assert progression.skill_points == 2

    response = progression_response(progression)
    assert response.next_level_xp == 110
    assert response.next_unlock == "Standard demand planning"
