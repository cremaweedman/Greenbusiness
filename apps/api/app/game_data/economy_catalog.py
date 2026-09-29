from __future__ import annotations

from dataclasses import dataclass

ECONOMY_CONFIG_VERSION = "economy_v1"
STARTING_CASH = 500


@dataclass(frozen=True)
class ContractDefinition:
    key: str
    title: str
    item_key: str
    item_name: str
    required_quantity: int
    reward_cash: int


@dataclass(frozen=True)
class UpgradeDefinition:
    key: str
    name: str
    cost_cash: int
    yield_bonus: int


STARTER_CONTRACT = ContractDefinition(
    key="neighborhood-sampler",
    title="Neighborhood Sampler",
    item_key="starter_crop.aurora-drift",
    item_name="Aurora Drift",
    required_quantity=3,
    reward_cash=150,
)

STARTER_UPGRADE = UpgradeDefinition(
    key="starter-yield-boost",
    name="Efficient Racks",
    cost_cash=600,
    yield_bonus=1,
)

CONTRACT_BY_KEY = {STARTER_CONTRACT.key: STARTER_CONTRACT}
UPGRADE_BY_KEY = {STARTER_UPGRADE.key: STARTER_UPGRADE}
