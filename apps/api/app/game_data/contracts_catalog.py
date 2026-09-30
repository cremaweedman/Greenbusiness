from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StarterContract:
    key: str
    name: str
    tier: str
    description: str
    item_key: str
    quantity: int
    quality_required: str | None
    cash_reward: int
    reputation_reward: int


@dataclass(frozen=True)
class ContractsCatalog:
    version: str
    contracts: tuple[StarterContract, ...]


CONTRACT_TIERS = {"quick", "standard", "premium"}
CATALOG_PATH = Path(__file__).with_name("starter_contracts.json")


def _require_text(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Contract field {field!r} must be a non-empty string.")
    return value.strip()


def _require_positive_int(raw: dict[str, Any], field: str) -> int:
    value = raw.get(field)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Contract field {field!r} must be a positive integer.")
    return value


def load_contracts_catalog(path: Path = CATALOG_PATH) -> ContractsCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Contracts catalog requires a non-empty version.")

    raw_contracts = payload.get("contracts")
    if not isinstance(raw_contracts, list) or not raw_contracts:
        raise ValueError("Contracts catalog requires at least one contract.")

    seen: set[str] = set()
    contracts: list[StarterContract] = []
    for raw in raw_contracts:
        if not isinstance(raw, dict):
            raise TypeError("Every contract entry must be an object.")
        key = _require_text(raw, "key")
        if key in seen:
            raise ValueError(f"Duplicate contract key: {key}")
        seen.add(key)

        tier = _require_text(raw, "tier")
        if tier not in CONTRACT_TIERS:
            raise ValueError(f"Unsupported contract tier: {tier}")

        quality_required = raw.get("quality_required")
        if quality_required is not None and not isinstance(quality_required, str):
            raise ValueError("quality_required must be null or a string.")

        contracts.append(
            StarterContract(
                key=key,
                name=_require_text(raw, "name"),
                tier=tier,
                description=_require_text(raw, "description"),
                item_key=_require_text(raw, "item_key"),
                quantity=_require_positive_int(raw, "quantity"),
                quality_required=quality_required,
                cash_reward=_require_positive_int(raw, "cash_reward"),
                reputation_reward=_require_positive_int(raw, "reputation_reward"),
            )
        )

    return ContractsCatalog(version=version.strip(), contracts=tuple(contracts))


STARTER_CONTRACTS_CATALOG = load_contracts_catalog()
STARTER_CONTRACTS = STARTER_CONTRACTS_CATALOG.contracts
STARTER_CONTRACT_BY_KEY = {contract.key: contract for contract in STARTER_CONTRACTS}
