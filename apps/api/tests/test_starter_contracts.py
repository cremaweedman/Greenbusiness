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
        assert contract.reputation_reward > 0
        assert "weed" not in contract.name.lower()


def test_starter_contract_rewards_are_bounded_by_unique_contracts():
    total_cash_available_once = sum(contract.cash_reward for contract in STARTER_CONTRACTS)
    assert total_cash_available_once == 270
    assert len({contract.key for contract in STARTER_CONTRACTS}) == len(STARTER_CONTRACTS)
