from __future__ import annotations

from app.game_data.contracts_catalog import (
    CONTRACT_TIERS,
    STARTER_CONTRACT_BY_KEY,
    STARTER_CONTRACTS,
    STARTER_CONTRACTS_CATALOG,
)


def test_starter_contracts_are_data_driven_and_versioned():
    assert STARTER_CONTRACTS_CATALOG.version == "p3-contracts-v1"
    assert [contract.tier for contract in STARTER_CONTRACTS] == ["quick", "standard", "premium"]
    assert len(STARTER_CONTRACT_BY_KEY) == len(STARTER_CONTRACTS)


def test_starter_contracts_have_safe_requirements_and_rewards():
    for contract in STARTER_CONTRACTS:
        assert contract.tier in CONTRACT_TIERS
        assert contract.item_key.startswith("starter_crop.")
        assert contract.quantity > 0
        assert contract.cash_reward > 0
        assert "weed" not in contract.name.lower()
