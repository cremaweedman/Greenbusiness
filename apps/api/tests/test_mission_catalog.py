from __future__ import annotations

import uuid
from datetime import date

from app.game_data.mission_catalog import (
    CONTACTS,
    MISSION_CONFIG_VERSION,
    MISSIONS,
    daily_pool_keys,
    weekly_pool_keys,
)


def test_starter_mission_catalog_is_versioned_and_coherent():
    assert MISSION_CONFIG_VERSION == "missions_v2"
    assert len(MISSIONS) == 30
    assert [mission.sequence for mission in MISSIONS] == list(range(1, 31))
    assert len({mission.key for mission in MISSIONS}) == 30
    assert {mission.objective_type for mission in MISSIONS} >= {
        "plant",
        "care",
        "harvest",
        "contract_complete",
        "cash_earned",
        "upgrade_owned",
    }
    assert len(CONTACTS) == 4
    assert len({contact.key for contact in CONTACTS}) == 4
    assert len({mission.arc_key for mission in MISSIONS}) >= 3
    assert all(mission.arc_title for mission in MISSIONS)
    assert all(mission.inbox_message for mission in MISSIONS)
    assert sum(mission.reward_cash for mission in MISSIONS) <= 3000


def test_daily_and_weekly_pools_are_deterministic():
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    day = date(2026, 9, 30)

    assert daily_pool_keys(user_id, day) == daily_pool_keys(user_id, day)
    assert weekly_pool_keys(user_id, day) == weekly_pool_keys(user_id, day)
    assert len(daily_pool_keys(user_id, day)) == 2
    assert len(weekly_pool_keys(user_id, day)) == 3
