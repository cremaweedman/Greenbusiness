from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    ContractCompletion,
    CurrencyLedgerEntry,
    InventoryContainer,
    InventoryItem,
)
from app.errors import AppError
from app.game_data.contracts_catalog import (
    STARTER_CONTRACT_BY_KEY,
    STARTER_CONTRACTS,
    STARTER_CONTRACTS_CATALOG,
    StarterContract,
)
from app.production_service import inventory_responses
from app.schemas import (
    ContractCompletionResponse,
    ContractRequirementResponse,
    ContractResponse,
    InventoryItemResponse,
)

CASH_CURRENCY = "cash"
CONTRACT_SOURCE = "contract_completion"
CONTRACT_COMPLETION_CONSTRAINT = "uq_contract_completion_user_contract"


def _display_name(item_key: str) -> str:
    prefix = "starter_crop."
    if item_key.startswith(prefix):
        return item_key.removeprefix(prefix).replace("-", " ").title()
    return item_key.replace("_", " ").replace(".", " ").title()


def _quantity_for_item(items: list[InventoryItemResponse], item_key: str) -> int:
    for item in items:
        if item.item_key == item_key:
            return item.quantity
    return 0


async def cash_balance(session: AsyncSession, user_id: uuid.UUID) -> int:
    entry = await session.scalar(
        select(CurrencyLedgerEntry)
        .where(CurrencyLedgerEntry.user_id == user_id)
        .where(CurrencyLedgerEntry.currency == CASH_CURRENCY)
        .order_by(desc(CurrencyLedgerEntry.created_at), desc(CurrencyLedgerEntry.id))
        .limit(1)
    )
    return entry.balance_after if entry is not None else 0


async def _completed_contract_keys(session: AsyncSession, user_id: uuid.UUID) -> set[str]:
    rows = await session.scalars(
        select(ContractCompletion.contract_key).where(ContractCompletion.user_id == user_id)
    )
    return set(rows.all())


def _contract_response(
    contract: StarterContract,
    *,
    inventory: list[InventoryItemResponse],
    completed_keys: set[str],
) -> ContractResponse:
    owned_quantity = _quantity_for_item(inventory, contract.item_key)
    completed = contract.key in completed_keys
    return ContractResponse(
        key=contract.key,
        name=contract.name,
        tier=contract.tier,
        description=contract.description,
        requirement=ContractRequirementResponse(
            item_key=contract.item_key,
            display_name=_display_name(contract.item_key),
            quantity=contract.quantity,
            quality_required=contract.quality_required,
        ),
        cash_reward=contract.cash_reward,
        can_complete=not completed and owned_quantity >= contract.quantity,
        completed=completed,
    )


async def contract_responses(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    inventory_container_id: uuid.UUID,
) -> list[ContractResponse]:
    inventory = await inventory_responses(session, inventory_container_id)
    completed_keys = await _completed_contract_keys(session, user_id)
    return [
        _contract_response(contract, inventory=inventory, completed_keys=completed_keys)
        for contract in STARTER_CONTRACTS
    ]


async def _get_inventory(session: AsyncSession, user_id: uuid.UUID) -> InventoryContainer:
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id).with_for_update()
    )
    if inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player inventory is missing.", status_code=500)
    return inventory


async def _get_inventory_item(
    session: AsyncSession,
    *,
    inventory_id: uuid.UUID,
    item_key: str,
) -> InventoryItem:
    item = await session.scalar(
        select(InventoryItem)
        .where(InventoryItem.inventory_container_id == inventory_id)
        .where(InventoryItem.item_key == item_key)
        .with_for_update()
    )
    if item is None:
        raise AppError("CONTRACT_REQUIREMENT_MISSING", "Required inventory is missing.", status_code=409)
    return item


def _is_duplicate_contract_completion(exc: IntegrityError) -> bool:
    constraint_name = getattr(getattr(exc, "orig", None), "constraint_name", None)
    return (
        constraint_name == CONTRACT_COMPLETION_CONSTRAINT
        or CONTRACT_COMPLETION_CONSTRAINT in str(exc.orig)
    )


async def complete_contract(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    contract_key: str,
    request_id: str | None,
) -> ContractCompletionResponse:
    contract = STARTER_CONTRACT_BY_KEY.get(contract_key)
    if contract is None:
        raise AppError("CONTRACT_NOT_FOUND", "Contract is not available.", status_code=404)

    existing = await session.scalar(
        select(ContractCompletion)
        .where(ContractCompletion.user_id == user_id)
        .where(ContractCompletion.contract_key == contract.key)
        .with_for_update()
    )
    if existing is not None:
        raise AppError("CONTRACT_ALREADY_COMPLETED", "Contract has already been completed.", status_code=409)

    inventory = await _get_inventory(session, user_id)
    item = await _get_inventory_item(session, inventory_id=inventory.id, item_key=contract.item_key)
    if item.quantity < contract.quantity:
        raise AppError(
            "CONTRACT_REQUIREMENT_MISSING",
            "Not enough inventory for this contract.",
            status_code=409,
            details={"required": contract.quantity, "available": item.quantity},
        )

    now = datetime.now(UTC)
    balance_before = await cash_balance(session, user_id)
    balance_after = balance_before + contract.cash_reward

    item.quantity -= contract.quantity
    completion = ContractCompletion(
        user_id=user_id,
        contract_key=contract.key,
        item_key=contract.item_key,
        quantity=contract.quantity,
        quality_required=contract.quality_required,
        cash_reward=contract.cash_reward,
        config_version=STARTER_CONTRACTS_CATALOG.version,
        completed_at=now,
    )
    ledger_entry = CurrencyLedgerEntry(
        user_id=user_id,
        currency=CASH_CURRENCY,
        source=CONTRACT_SOURCE,
        source_id=contract.key,
        amount=contract.cash_reward,
        balance_before=balance_before,
        balance_after=balance_after,
        config_version=STARTER_CONTRACTS_CATALOG.version,
    )
    session.add_all([completion, ledger_entry])
    await append_audit_event(
        session,
        event_type="contracts.contract_completed",
        actor_type="user",
        actor_id=str(user_id),
        target_type="contract",
        target_id=contract.key,
        request_id=request_id,
        payload={
            "item_key": contract.item_key,
            "quantity": contract.quantity,
            "cash_reward": contract.cash_reward,
            "balance_after": balance_after,
            "config_version": STARTER_CONTRACTS_CATALOG.version,
        },
    )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if _is_duplicate_contract_completion(exc):
            raise AppError(
                "CONTRACT_ALREADY_COMPLETED",
                "Contract has already been completed.",
                status_code=409,
            ) from exc
        raise

    updated_inventory = await inventory_responses(session, inventory.id)
    completed_keys = await _completed_contract_keys(session, user_id)
    return ContractCompletionResponse(
        contract=_contract_response(contract, inventory=updated_inventory, completed_keys=completed_keys),
        inventory=updated_inventory,
        cash_balance=balance_after,
        cash_delta=contract.cash_reward,
    )
