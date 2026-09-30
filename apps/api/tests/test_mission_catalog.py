from __future__ import annotations

import uuid
from datetime import date

from app.game_data.mission_catalog import (
    CONTACTS,
    MISSIONS,
    MISSION_CONFIG_VERSION,
    daily_pool_keys,
    weekly_pool_keys,
)


def test_starter_mission_catalog_is_versioned_and_coherent():
    assert MISSION_CONFIG_VERSION == "missions_v1"
    assert len(MISSIONS) == 10
    assert [mission.sequence for mission in MISSIONS] == list(range(1, 11))
    assert len({mission.key for mission in MISSIONS}) == 10
    assert {mission.objective_type for mission in MISSIONS} >= {
        "plant",
        "care",
        "harvest",
        "contract_complete",
        "cash_earned",
        "upgrade_owned",
    }
    assert len(CONTACTS) == 2
    assert len({contact.key for contact in CONTACTS}) == 2


def test_daily_and_weekly_pools_are_deterministic():
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000123")
    day = date(2026, 9, 30)

    assert daily_pool_keys(user_id, day) == daily_pool_keys(user_id, day)
    assert weekly_pool_keys(user_id, day) == weekly_pool_keys(user_id, day)
    assert len(daily_pool_keys(user_id, day)) == 2
    assert len(weekly_pool_keys(user_id, day)) == 3
