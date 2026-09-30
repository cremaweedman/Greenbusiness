from __future__ import annotations

from app.game_data.upgrades_catalog import (
    STARTER_UPGRADE_BY_KEY,
    STARTER_UPGRADES,
    STARTER_UPGRADES_CATALOG,
)


def test_starter_upgrades_are_data_driven_and_versioned():
    assert STARTER_UPGRADES_CATALOG.version == "p3-upgrades-v1"
    assert [upgrade.key for upgrade in STARTER_UPGRADES] == [
        "starter-bench-calibration",
        "starter-room-expansion",
    ]
    assert len(STARTER_UPGRADE_BY_KEY) == len(STARTER_UPGRADES)


def test_starter_upgrade_creates_cash_sink_and_production_change():
    upgrade = STARTER_UPGRADES[0]
    assert upgrade.cash_cost == 100
    assert upgrade.max_level == 1
    assert upgrade.effects.yield_bonus == 1
    assert upgrade.effects.slot_capacity_bonus == 0


def test_starter_capacity_upgrade_adds_a_production_slot():
    upgrade = STARTER_UPGRADE_BY_KEY["starter-room-expansion"]
    assert upgrade.cash_cost == 120
    assert upgrade.max_level == 1
    assert upgrade.effects.yield_bonus == 0
    assert upgrade.effects.slot_capacity_bonus == 1
