from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    EconomyLedger,
    EconomyRequest,
    InventoryContainer,
    InventoryItem,
    PlayerContract,
    PlayerUpgrade,
    Wallet,
)
from app.errors import AppError
from app.game_data.economy_catalog import (
    CONTRACT_BY_KEY,
    ECONOMY_CONFIG_VERSION,
    STARTER_CONTRACT,
    STARTER_UPGRADE,
    STARTING_CASH,
    UPGRADE_BY_KEY,
)
from app.production_service import inventory_responses
from app.schemas import (
    ContractOfferResponse,
    EconomyActionResponse,
    PlayerContractResponse,
    UpgradeOfferResponse,
)


async def bootstrap_wallet(session: AsyncSession, user_id: uuid.UUID) -> Wallet:
    wallet = Wallet(user_id=user_id, cash=STARTING_CASH)
    session.add(wallet)
    await session.flush()
    session.add(
        EconomyLedger(
            transaction_id=uuid.uuid4(),
            user_id=user_id,
            currency="cash",
            amount=STARTING_CASH,
            source_or_sink="bootstrap",
            reference_type="user",
            reference_id=str(user_id),
            config_version=ECONOMY_CONFIG_VERSION,
            balance_before=0,
            balance_after=STARTING_CASH,
        )
    )
    return wallet


async def _wallet_for_update(session: AsyncSession, user_id: uuid.UUID) -> Wallet:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id).with_for_update())
    if wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player wallet is missing.", status_code=500)
    return wallet


async def _inventory_for_update(session: AsyncSession, user_id: uuid.UUID) -> InventoryContainer:
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id).with_for_update()
    )
    if inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player inventory is missing.", status_code=500)
    return inventory


async def _owned_upgrade_keys(session: AsyncSession, user_id: uuid.UUID) -> list[str]:
    return list(
        (
            await session.scalars(
                select(PlayerUpgrade.upgrade_key)
                .where(PlayerUpgrade.user_id == user_id)
                .order_by(PlayerUpgrade.upgrade_key)
            )
        ).all()
    )


def contract_offer_response() -> ContractOfferResponse:
    contract = STARTER_CONTRACT
    return ContractOfferResponse(
        key=contract.key,
        title=contract.title,
        item_key=contract.item_key,
        item_name=contract.item_name,
        required_quantity=contract.required_quantity,
        reward_cash=contract.reward_cash,
    )


def upgrade_offer_response() -> UpgradeOfferResponse:
    upgrade = STARTER_UPGRADE
    return UpgradeOfferResponse(
        key=upgrade.key,
        name=upgrade.name,
        cost_cash=upgrade.cost_cash,
        yield_bonus=upgrade.yield_bonus,
    )


def _contract_response(contract: PlayerContract | None) -> PlayerContractResponse | None:
    if contract is None:
        return None
    return PlayerContractResponse(
        id=contract.id,
        contract_key=contract.contract_key,
        status=contract.status,
        accepted_at=contract.accepted_at,
        completed_at=contract.completed_at,
    )


async def economy_state(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> tuple[int, list[ContractOfferResponse], PlayerContractResponse | None, list[UpgradeOfferResponse], list[str]]:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    if wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player wallet is missing.", status_code=500)

    contract = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.user_id == user_id)
        .where(PlayerContract.contract_key == STARTER_CONTRACT.key)
    )
    offers = [] if contract is not None else [contract_offer_response()]
    upgrades = [] if STARTER_UPGRADE.key in await _owned_upgrade_keys(session, user_id) else [
        upgrade_offer_response()
    ]
    return (
        wallet.cash,
        offers,
        _contract_response(contract),
        upgrades,
        await _owned_upgrade_keys(session, user_id),
    )


async def _check_idempotency(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    idempotency_key: str,
    operation: str,
    reference_id: str,
) -> bool:
    existing = await session.scalar(
        select(EconomyRequest)
        .where(EconomyRequest.user_id == user_id)
        .where(EconomyRequest.idempotency_key == idempotency_key)
    )
    if existing is None:
        return False
    if existing.operation != operation or existing.reference_id != reference_id:
        raise AppError(
            "ECONOMY_IDEMPOTENCY_CONFLICT",
            "Idempotency key was already used for another operation.",
            status_code=409,
        )
    return True


async def _action_response(session: AsyncSession, user_id: uuid.UUID) -> EconomyActionResponse:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id)
    )
    contract = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.user_id == user_id)
        .where(PlayerContract.contract_key == STARTER_CONTRACT.key)
    )
    if wallet is None or inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player economic state is incomplete.", status_code=500)
    return EconomyActionResponse(
        cash=wallet.cash,
        inventory=await inventory_responses(session, inventory.id),
        active_contract=_contract_response(contract),
        owned_upgrade_keys=await _owned_upgrade_keys(session, user_id),
    )


async def accept_contract(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    contract_key: str,
    request_id: str | None,
) -> PlayerContractResponse:
    definition = CONTRACT_BY_KEY.get(contract_key)
    if definition is None:
        raise AppError("CONTRACT_NOT_FOUND", "Contract offer not found.", status_code=404)

    existing = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.user_id == user_id)
        .where(PlayerContract.contract_key == contract_key)
        .with_for_update()
    )
    if existing is not None:
        if existing.status == "active":
            return _contract_response(existing)  # type: ignore[return-value]
        raise AppError("CONTRACT_ALREADY_COMPLETED", "Contract is already completed.", status_code=409)

    contract = PlayerContract(
        user_id=user_id,
        contract_key=definition.key,
        status="active",
        accepted_at=datetime.now(UTC),
    )
    session.add(contract)
    await append_audit_event(
        session,
        event_type="economy.contract_accepted",
        actor_type="user",
        actor_id=str(user_id),
        target_type="contract",
        target_id=definition.key,
        request_id=request_id,
    )
    await session.commit()
    return _contract_response(contract)  # type: ignore[return-value]


async def complete_contract(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    contract_id: uuid.UUID,
    idempotency_key: str,
    request_id: str | None,
) -> EconomyActionResponse:
    reference_id = str(contract_id)
    if await _check_idempotency(
        session,
        user_id=user_id,
        idempotency_key=idempotency_key,
        operation="contract.complete",
        reference_id=reference_id,
    ):
        return await _action_response(session, user_id)

    contract = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.id == contract_id)
        .where(PlayerContract.user_id == user_id)
        .with_for_update()
    )
    if contract is None:
        raise AppError("CONTRACT_NOT_FOUND", "Contract not found.", status_code=404)
    if contract.status != "active":
        raise AppError("CONTRACT_ALREADY_COMPLETED", "Contract is already completed.", status_code=409)

    definition = CONTRACT_BY_KEY.get(contract.contract_key)
    if definition is None:
        raise AppError("CONTRACT_CONFIG_MISSING", "Contract configuration is missing.", status_code=500)

    inventory = await _inventory_for_update(session, user_id)
    item = await session.scalar(
        select(InventoryItem)
        .where(InventoryItem.inventory_container_id == inventory.id)
        .where(InventoryItem.item_key == definition.item_key)
        .with_for_update()
    )
    if item is None or item.quantity < definition.required_quantity:
        raise AppError(
            "CONTRACT_INVENTORY_INSUFFICIENT",
            "Not enough inventory to complete this contract.",
            status_code=409,
            details={"required_quantity": definition.required_quantity},
        )

    wallet = await _wallet_for_update(session, user_id)
    before = wallet.cash
    after = before + definition.reward_cash
    item.quantity -= definition.required_quantity
    wallet.cash = after
    contract.status = "completed"
    contract.completed_at = datetime.now(UTC)

    transaction_id = uuid.uuid4()
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=definition.reward_cash,
            source_or_sink="contract_reward",
            reference_type="contract",
            reference_id=str(contract.id),
            config_version=ECONOMY_CONFIG_VERSION,
            balance_before=before,
            balance_after=after,
        )
    )
    session.add(
        EconomyRequest(
            user_id=user_id,
            idempotency_key=idempotency_key,
            operation="contract.complete",
            reference_id=reference_id,
        )
    )
    await append_audit_event(
        session,
        event_type="economy.contract_completed",
        actor_type="user",
        actor_id=str(user_id),
        target_type="player_contract",
        target_id=str(contract.id),
        request_id=request_id,
        payload={"cash_reward": definition.reward_cash, "transaction_id": str(transaction_id)},
    )
    await session.commit()
    return await _action_response(session, user_id)


async def purchase_upgrade(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    upgrade_key: str,
    idempotency_key: str,
    request_id: str | None,
) -> EconomyActionResponse:
    definition = UPGRADE_BY_KEY.get(upgrade_key)
    if definition is None:
        raise AppError("UPGRADE_NOT_FOUND", "Upgrade not found.", status_code=404)

    if await _check_idempotency(
        session,
        user_id=user_id,
        idempotency_key=idempotency_key,
        operation="upgrade.purchase",
        reference_id=upgrade_key,
    ):
        return await _action_response(session, user_id)

    existing = await session.scalar(
        select(PlayerUpgrade)
        .where(PlayerUpgrade.user_id == user_id)
        .where(PlayerUpgrade.upgrade_key == upgrade_key)
    )
    if existing is not None:
        raise AppError("UPGRADE_ALREADY_OWNED", "Upgrade is already owned.", status_code=409)

    wallet = await _wallet_for_update(session, user_id)
    if wallet.cash < definition.cost_cash:
        raise AppError(
            "ECONOMY_CASH_INSUFFICIENT",
            "Not enough Cash for this upgrade.",
            status_code=409,
            details={"required_cash": definition.cost_cash, "cash": wallet.cash},
        )

    before = wallet.cash
    after = before - definition.cost_cash
    wallet.cash = after
    upgrade = PlayerUpgrade(user_id=user_id, upgrade_key=upgrade_key)
    session.add(upgrade)

    transaction_id = uuid.uuid4()
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=-definition.cost_cash,
            source_or_sink="upgrade_purchase",
            reference_type="upgrade",
            reference_id=upgrade_key,
            config_version=ECONOMY_CONFIG_VERSION,
            balance_before=before,
            balance_after=after,
        )
    )
    session.add(
        EconomyRequest(
            user_id=user_id,
            idempotency_key=idempotency_key,
            operation="upgrade.purchase",
            reference_id=upgrade_key,
        )
    )
    await append_audit_event(
        session,
        event_type="economy.upgrade_purchased",
        actor_type="user",
        actor_id=str(user_id),
        target_type="upgrade",
        target_id=upgrade_key,
        request_id=request_id,
        payload={"cash_cost": definition.cost_cash, "transaction_id": str(transaction_id)},
    )
    await session.commit()
    return await _action_response(session, user_id)
