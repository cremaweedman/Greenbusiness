from __future__ import annotations

from dataclasses import dataclass

ECONOMY_CONFIG_VERSION = "economy_v2"
STARTING_CASH = 500
CONTRACT_REFRESH_SECONDS = 14_400
STANDARD_OFFER_COUNT = 3
SPECIALIZED_OFFER_COUNT = 1
MAX_ACTIVE_CONTRACTS = 3


@dataclass(frozen=True)
class ContractDefinition:
    key: str
    title: str
    archetype: str
    item_key: str
    item_name: str
    required_quantity: int
    reward_cash: int
    reward_reputation: int
    min_level: int = 1
    min_reputation: int = 0
    required_quality: str | None = None
    required_trait: str | None = None
    specialized: bool = False


@dataclass(frozen=True)
class UpgradeDefinition:
    key: str
    name: str
    tier: int
    cost_cash: int
    yield_bonus: int
    min_level: int = 1
    prerequisite_key: str | None = None


CONTRACTS = (
    ContractDefinition(
        key="neighborhood-sampler",
        title="Neighborhood Sampler",
        archetype="quick",
        item_key="starter_crop.aurora-drift",
        item_name="Aurora Drift",
        required_quantity=3,
        reward_cash=150,
        reward_reputation=5,
    ),
    ContractDefinition(
        key="corner-cafe-order",
        title="Corner Cafe Order",
        archetype="quick",
        item_key="starter_crop.ember-leaf",
        item_name="Ember Leaf",
        required_quantity=4,
        reward_cash=220,
        reward_reputation=6,
    ),
    ContractDefinition(
        key="moonlight-batch",
        title="Moonlight Batch",
        archetype="standard",
        item_key="starter_crop.moon-sprout",
        item_name="Moon Sprout",
        required_quantity=5,
        reward_cash=320,
        reward_reputation=8,
    ),
    ContractDefinition(
        key="careful-client",
        title="Careful Client",
        archetype="standard",
        item_key="starter_crop.aurora-drift",
        item_name="Aurora Drift",
        required_quantity=4,
        reward_cash=260,
        reward_reputation=8,
        required_quality="cared",
    ),
    ContractDefinition(
        key="fast-turnaround",
        title="Fast Turnaround",
        archetype="standard",
        item_key="starter_crop.aurora-drift",
        item_name="Aurora Drift",
        required_quantity=3,
        reward_cash=200,
        reward_reputation=7,
        required_trait="fast",
    ),
    ContractDefinition(
        key="stable-supply",
        title="Stable Supply",
        archetype="standard",
        item_key="starter_crop.ember-leaf",
        item_name="Ember Leaf",
        required_quantity=5,
        reward_cash=300,
        reward_reputation=10,
        required_trait="stable",
        min_level=2,
    ),
    ContractDefinition(
        key="premium-night-run",
        title="Premium Night Run",
        archetype="premium",
        item_key="starter_crop.moon-sprout",
        item_name="Moon Sprout",
        required_quantity=6,
        reward_cash=430,
        reward_reputation=14,
        required_quality="cared",
        min_level=3,
        min_reputation=12,
    ),
    ContractDefinition(
        key="specialist-aurora",
        title="Specialist: Aurora Drift",
        archetype="premium",
        item_key="starter_crop.aurora-drift",
        item_name="Aurora Drift",
        required_quantity=6,
        reward_cash=420,
        reward_reputation=16,
        required_quality="cared",
        required_trait="fast",
        min_level=3,
        min_reputation=10,
        specialized=True,
    ),
    ContractDefinition(
        key="specialist-ember",
        title="Specialist: Ember Leaf",
        archetype="premium",
        item_key="starter_crop.ember-leaf",
        item_name="Ember Leaf",
        required_quantity=7,
        reward_cash=500,
        reward_reputation=18,
        required_quality="cared",
        required_trait="stable",
        min_level=4,
        min_reputation=18,
        specialized=True,
    ),
    ContractDefinition(
        key="specialist-moon",
        title="Specialist: Moon Sprout",
        archetype="premium",
        item_key="starter_crop.moon-sprout",
        item_name="Moon Sprout",
        required_quantity=8,
        reward_cash=620,
        reward_reputation=22,
        required_quality="cared",
        required_trait="premium",
        min_level=5,
        min_reputation=28,
        specialized=True,
    ),
)

CONTRACT_BY_KEY = {contract.key: contract for contract in CONTRACTS}

STARTER_CONTRACT = CONTRACT_BY_KEY["neighborhood-sampler"]

UPGRADES = (
    UpgradeDefinition(
        key="starter-yield-boost",
        name="Efficient Racks I",
        tier=1,
        cost_cash=600,
        yield_bonus=1,
    ),
    UpgradeDefinition(
        key="efficient-racks-2",
        name="Efficient Racks II",
        tier=2,
        cost_cash=1080,
        yield_bonus=1,
        min_level=4,
        prerequisite_key="starter-yield-boost",
    ),
    UpgradeDefinition(
        key="efficient-racks-3",
        name="Efficient Racks III",
        tier=3,
        cost_cash=1944,
        yield_bonus=1,
        min_level=8,
        prerequisite_key="efficient-racks-2",
    ),
)

UPGRADE_BY_KEY = {upgrade.key: upgrade for upgrade in UPGRADES}
STARTER_UPGRADE = UPGRADE_BY_KEY["starter-yield-boost"]
