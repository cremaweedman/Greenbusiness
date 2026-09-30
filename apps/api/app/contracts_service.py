from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    ContractCompletion,
    CurrencyLedgerEntry,
    InventoryContainer,
    InventoryItem,
    PlayerContractBoard,
    Progression,
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
    ContractBoardResponse,
    ContractCompletionResponse,
    ContractRequirementResponse,
    ContractRerollResponse,
    ContractResponse,
    CurrencyLedgerEntryResponse,
    EconomySummaryResponse,
    InventoryItemResponse,
)
from app.skills_service import player_skill_effects

CASH_CURRENCY = "cash"
CONTRACT_SOURCE = "contract_completion"
CONTRACT_REROLL_SOURCE = "contract_reroll"
CONTRACT_COMPLETION_CONSTRAINT = "uq_contract_completion_user_contract"
CONTRACT_BOARD_SIZE = 2
CONTRACT_REROLL_COST = 25
CONTRACT_REROLL_LIMIT = 3
CONTRACT_REROLL_WINDOW = timedelta(hours=24)


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


async def cash_ledger_entries(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    limit: int = 10,
) -> list[CurrencyLedgerEntryResponse]:
    entries = (
        await session.scalars(
            select(CurrencyLedgerEntry)
            .where(CurrencyLedgerEntry.user_id == user_id)
            .where(CurrencyLedgerEntry.currency == CASH_CURRENCY)
            .order_by(desc(CurrencyLedgerEntry.created_at), desc(CurrencyLedgerEntry.id))
            .limit(limit)
        )
    ).all()
    return [
        CurrencyLedgerEntryResponse(
            id=entry.id,
            currency=entry.currency,
            source=entry.source,
            source_id=entry.source_id,
            amount=entry.amount,
            balance_before=entry.balance_before,
            balance_after=entry.balance_after,
            config_version=entry.config_version,
            created_at=entry.created_at,
        )
        for entry in entries
    ]


async def cash_summary(session: AsyncSession, *, user_id: uuid.UUID) -> EconomySummaryResponse:
    entries = (
        await session.scalars(
            select(CurrencyLedgerEntry)
            .where(CurrencyLedgerEntry.user_id == user_id)
            .where(CurrencyLedgerEntry.currency == CASH_CURRENCY)
            .order_by(CurrencyLedgerEntry.created_at, CurrencyLedgerEntry.id)
        )
    ).all()
    minted = sum(entry.amount for entry in entries if entry.amount > 0)
    burned = sum(abs(entry.amount) for entry in entries if entry.amount < 0)
    balance = entries[-1].balance_after if entries else 0
    config_versions = sorted({entry.config_version for entry in entries})
    return EconomySummaryResponse(
        currency=CASH_CURRENCY,
        balance=balance,
        minted=minted,
        burned=burned,
        entry_count=len(entries),
        config_versions=config_versions,
    )


async def _completed_contract_keys(session: AsyncSession, user_id: uuid.UUID) -> set[str]:
    rows = await session.scalars(
        select(ContractCompletion.contract_key).where(ContractCompletion.user_id == user_id)
    )
    return set(rows.all())


def _initial_offer_keys() -> list[str]:
    return [contract.key for contract in STARTER_CONTRACTS[:CONTRACT_BOARD_SIZE]]


def _rotated_offer_keys(reroll_count: int) -> list[str]:
    keys = [contract.key for contract in STARTER_CONTRACTS]
    start = (reroll_count * CONTRACT_BOARD_SIZE) % len(keys)
    return [keys[(start + offset) % len(keys)] for offset in range(CONTRACT_BOARD_SIZE)]


def _window_expired(board: PlayerContractBoard, now: datetime) -> bool:
    return board.window_started_at + CONTRACT_REROLL_WINDOW <= now


async def _get_contract_board(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    for_update: bool = False,
) -> PlayerContractBoard | None:
    statement = select(PlayerContractBoard).where(PlayerContractBoard.user_id == user_id)
    if for_update:
        statement = statement.with_for_update()
    return await session.scalar(statement)


def _contract_response(
    contract: StarterContract,
    *,
    inventory: list[InventoryItemResponse],
    completed_keys: set[str],
    cash_bonus: int = 0,
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
        cash_reward=contract.cash_reward + cash_bonus,
        reputation_reward=contract.reputation_reward,
        can_complete=not completed and owned_quantity >= contract.quantity,
        completed=completed,
    )


async def contract_responses(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    inventory_container_id: uuid.UUID,
) -> list[ContractResponse]:
    board = await contract_board_response(
        session,
        user_id=user_id,
        inventory_container_id=inventory_container_id,
    )
    return board.contracts


async def contract_board_response(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    inventory_container_id: uuid.UUID,
) -> ContractBoardResponse:
    now = datetime.now(UTC)
    board = await _get_contract_board(session, user_id=user_id)
    offer_keys = _initial_offer_keys()
    reroll_count = 0
    window_started_at = now
    if board is not None and not _window_expired(board, now):
        offer_keys = list(board.offer_keys)
        reroll_count = board.reroll_count
        window_started_at = board.window_started_at
    inventory = await inventory_responses(session, inventory_container_id)
    completed_keys = await _completed_contract_keys(session, user_id)
    skill_effects = await player_skill_effects(session, user_id=user_id)
    offers = [
        _contract_response(
            STARTER_CONTRACT_BY_KEY[contract_key],
            inventory=inventory,
            completed_keys=completed_keys,
            cash_bonus=skill_effects.contract_cash_bonus,
        )
        for contract_key in offer_keys
        if contract_key in STARTER_CONTRACT_BY_KEY
    ]
    return ContractBoardResponse(
        contracts=offers,
        reroll_cost=CONTRACT_REROLL_COST,
        rerolls_used=reroll_count,
        rerolls_remaining=max(0, CONTRACT_REROLL_LIMIT - reroll_count),
        window_started_at=window_started_at,
    )


async def list_contracts(session: AsyncSession, *, user_id: uuid.UUID) -> list[ContractResponse]:
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id)
    )
    if inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player inventory is missing.", status_code=500)
    return await contract_responses(
        session,
        user_id=user_id,
        inventory_container_id=inventory.id,
    )


async def get_contract_board(session: AsyncSession, *, user_id: uuid.UUID) -> ContractBoardResponse:
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id)
    )
    if inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player inventory is missing.", status_code=500)
    return await contract_board_response(
        session,
        user_id=user_id,
        inventory_container_id=inventory.id,
    )


async def reroll_contract_board(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    request_id: str | None,
) -> ContractRerollResponse:
    inventory = await _get_inventory(session, user_id)
    now = datetime.now(UTC)
    board = await _get_contract_board(session, user_id=user_id, for_update=True)
    if board is None:
        board = PlayerContractBoard(
            user_id=user_id,
            offer_keys=_initial_offer_keys(),
            reroll_count=0,
            window_started_at=now,
            updated_at=now,
        )
        session.add(board)
        await session.flush()
    elif _window_expired(board, now):
        board.offer_keys = _initial_offer_keys()
        board.reroll_count = 0
        board.window_started_at = now

    if board.reroll_count >= CONTRACT_REROLL_LIMIT:
        raise AppError("CONTRACT_REROLL_LIMIT", "Contract reroll limit reached.", status_code=409)

    balance_before = await cash_balance(session, user_id)
    if balance_before < CONTRACT_REROLL_COST:
        raise AppError(
            "CONTRACT_REROLL_CASH_INSUFFICIENT",
            "Not enough Cash to reroll contracts.",
            status_code=409,
            details={"required": CONTRACT_REROLL_COST, "available": balance_before},
        )

    next_count = board.reroll_count + 1
    balance_after = balance_before - CONTRACT_REROLL_COST
    board.reroll_count = next_count
    board.offer_keys = _rotated_offer_keys(next_count)
    board.updated_at = now
    ledger_entry = CurrencyLedgerEntry(
        user_id=user_id,
        currency=CASH_CURRENCY,
        source=CONTRACT_REROLL_SOURCE,
        source_id=f"{board.window_started_at.isoformat()}:{next_count}",
        amount=-CONTRACT_REROLL_COST,
        balance_before=balance_before,
        balance_after=balance_after,
        config_version=STARTER_CONTRACTS_CATALOG.version,
    )
    session.add(ledger_entry)
    await append_audit_event(
        session,
        event_type="contracts.contract_board_rerolled",
        actor_type="user",
        actor_id=str(user_id),
        target_type="contract_board",
        target_id=str(board.id),
        request_id=request_id,
        payload={
            "offer_keys": board.offer_keys,
            "reroll_count": board.reroll_count,
            "cash_cost": CONTRACT_REROLL_COST,
            "balance_after": balance_after,
        },
    )
    await session.commit()

    return ContractRerollResponse(
        board=await contract_board_response(
            session,
            user_id=user_id,
            inventory_container_id=inventory.id,
        ),
        cash_balance=balance_after,
        cash_delta=-CONTRACT_REROLL_COST,
        economy_summary=await cash_summary(session, user_id=user_id),
    )


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

    board = await _get_contract_board(session, user_id=user_id)
    active_offer_keys = (
        _initial_offer_keys()
        if board is None or _window_expired(board, datetime.now(UTC))
        else list(board.offer_keys)
    )
    if contract.key not in active_offer_keys:
        raise AppError("CONTRACT_NOT_OFFERED", "Contract is not on the active board.", status_code=409)

    inventory = await _get_inventory(session, user_id)
    item = await _get_inventory_item(session, inventory_id=inventory.id, item_key=contract.item_key)
    if item.quantity < contract.quantity:
        raise AppError(
            "CONTRACT_REQUIREMENT_MISSING",
            "Not enough inventory for this contract.",
            status_code=409,
            details={"required": contract.quantity, "available": item.quantity},
        )

    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)

    now = datetime.now(UTC)
    skill_effects = await player_skill_effects(session, user_id=user_id)
    cash_reward = contract.cash_reward + skill_effects.contract_cash_bonus
    balance_before = await cash_balance(session, user_id)
    balance_after = balance_before + cash_reward

    item.quantity -= contract.quantity
    completion = ContractCompletion(
        user_id=user_id,
        contract_key=contract.key,
        item_key=contract.item_key,
        quantity=contract.quantity,
        quality_required=contract.quality_required,
        cash_reward=cash_reward,
        reputation_reward=contract.reputation_reward,
        config_version=STARTER_CONTRACTS_CATALOG.version,
        completed_at=now,
    )
    ledger_entry = CurrencyLedgerEntry(
        user_id=user_id,
        currency=CASH_CURRENCY,
        source=CONTRACT_SOURCE,
        source_id=contract.key,
        amount=cash_reward,
        balance_before=balance_before,
        balance_after=balance_after,
        config_version=STARTER_CONTRACTS_CATALOG.version,
    )
    progression.reputation += contract.reputation_reward
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
            "cash_reward": cash_reward,
            "reputation_reward": contract.reputation_reward,
            "reputation": progression.reputation,
            "skill_contract_cash_bonus": skill_effects.contract_cash_bonus,
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
        contract=_contract_response(
            contract,
            inventory=updated_inventory,
            completed_keys=completed_keys,
            cash_bonus=skill_effects.contract_cash_bonus,
        ),
        inventory=updated_inventory,
        cash_balance=balance_after,
        cash_delta=cash_reward,
        reputation=progression.reputation,
        reputation_delta=contract.reputation_reward,
    )
