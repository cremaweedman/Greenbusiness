from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    EconomyLedger,
    EconomyRequest,
    InventoryContainer,
    InventoryItem,
    InventoryLot,
    PlayerContract,
    PlayerUpgrade,
    Progression,
    Wallet,
)
from app.errors import AppError
from app.game_data.economy_catalog import (
    CONTRACTS,
    CONTRACT_BY_KEY,
    CONTRACT_REFRESH_SECONDS,
    ECONOMY_CONFIG_VERSION,
    MAX_ACTIVE_CONTRACTS,
    SPECIALIZED_OFFER_COUNT,
    STANDARD_OFFER_COUNT,
    STARTER_CONTRACT,
    STARTING_CASH,
    UPGRADES,
    UPGRADE_BY_KEY,
    ContractDefinition,
    UpgradeDefinition,
)
from app.game_data.production_catalog import STARTER_VARIETY_BY_KEY
from app.production_service import inventory_lot_responses, inventory_responses
from app.schemas import (
    ContractOfferResponse,
    EconomyActionResponse,
    PlayerContractResponse,
    UpgradeOfferResponse,
)


@dataclass(frozen=True)
class EconomyState:
    cash: int
    contract_offers: list[ContractOfferResponse]
    contract_refresh_at: datetime
    active_contract: PlayerContractResponse | None
    active_contracts: list[PlayerContractResponse]
    upgrade_offers: list[UpgradeOfferResponse]
    owned_upgrade_keys: list[str]


def offer_bucket_for_time(now: datetime) -> int:
    return int(now.timestamp()) // CONTRACT_REFRESH_SECONDS


def refresh_at_for_bucket(bucket: int) -> datetime:
    return datetime.fromtimestamp((bucket + 1) * CONTRACT_REFRESH_SECONDS, tz=UTC)


def _rank(user_id: uuid.UUID, bucket: int, slot: int, key: str) -> str:
    raw = f"{ECONOMY_CONFIG_VERSION}:{user_id}:{bucket}:{slot}:{key}".encode()
    return hashlib.sha256(raw).hexdigest()


def _contract_locked(definition: ContractDefinition, *, level: int, reputation: int) -> bool:
    return level < definition.min_level or reputation < definition.min_reputation


def _offer_response(
    definition: ContractDefinition,
    *,
    user_id: uuid.UUID,
    bucket: int,
    slot: int,
    level: int,
    reputation: int,
) -> ContractOfferResponse:
    return ContractOfferResponse(
        offer_id=f"{bucket}-{slot}-{definition.key}",
        offer_bucket=bucket,
        key=definition.key,
        title=definition.title,
        archetype=definition.archetype,
        item_key=definition.item_key,
        item_name=definition.item_name,
        required_quantity=definition.required_quantity,
        required_quality=definition.required_quality,
        required_trait=definition.required_trait,
        reward_cash=definition.reward_cash,
        reward_reputation=definition.reward_reputation,
        min_level=definition.min_level,
        min_reputation=definition.min_reputation,
        specialized=definition.specialized,
        locked=_contract_locked(definition, level=level, reputation=reputation),
        expires_at=refresh_at_for_bucket(bucket),
    )


def generate_contract_offers(
    *,
    user_id: uuid.UUID,
    level: int,
    reputation: int,
    now: datetime,
) -> list[ContractOfferResponse]:
    bucket = offer_bucket_for_time(now)
    standards = [contract for contract in CONTRACTS if not contract.specialized]
    specialized = [contract for contract in CONTRACTS if contract.specialized]

    eligible = [
        contract
        for contract in standards
        if not _contract_locked(contract, level=level, reputation=reputation)
    ]
    locked = [
        contract
        for contract in standards
        if _contract_locked(contract, level=level, reputation=reputation)
    ]

    selected: list[ContractDefinition] = []
    if STARTER_CONTRACT in eligible:
        selected.append(STARTER_CONTRACT)

    eligible_rest = [contract for contract in eligible if contract not in selected]
    eligible_rest.sort(key=lambda contract: _rank(user_id, bucket, 0, contract.key))
    selected.extend(eligible_rest[: max(0, STANDARD_OFFER_COUNT - len(selected))])

    if len(selected) < STANDARD_OFFER_COUNT:
        locked.sort(key=lambda contract: _rank(user_id, bucket, 1, contract.key))
        selected.extend(locked[: STANDARD_OFFER_COUNT - len(selected)])

    offers = [
        _offer_response(
            contract,
            user_id=user_id,
            bucket=bucket,
            slot=slot,
            level=level,
            reputation=reputation,
        )
        for slot, contract in enumerate(selected[:STANDARD_OFFER_COUNT])
    ]

    specialized.sort(key=lambda contract: _rank(user_id, bucket, 2, contract.key))
    for index, contract in enumerate(specialized[:SPECIALIZED_OFFER_COUNT]):
        offers.append(
            _offer_response(
                contract,
                user_id=user_id,
                bucket=bucket,
                slot=STANDARD_OFFER_COUNT + index,
                level=level,
                reputation=reputation,
            )
        )
    return offers


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


async def _progression_for_update(session: AsyncSession, user_id: uuid.UUID) -> Progression:
    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)
    return progression


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
                .order_by(PlayerUpgrade.purchased_at, PlayerUpgrade.upgrade_key)
            )
        ).all()
    )


def _contract_response(contract: PlayerContract | None) -> PlayerContractResponse | None:
    if contract is None:
        return None
    return PlayerContractResponse(
        id=contract.id,
        offer_id=contract.offer_id,
        offer_bucket=contract.offer_bucket,
        contract_key=contract.contract_key,
        archetype=contract.archetype,
        item_key=contract.item_key,
        required_quantity=contract.required_quantity,
        required_quality=contract.required_quality,
        required_trait=contract.required_trait,
        reward_cash=contract.reward_cash,
        reward_reputation=contract.reward_reputation,
        status=contract.status,
        accepted_at=contract.accepted_at,
        completed_at=contract.completed_at,
    )


def _upgrade_response(
    definition: UpgradeDefinition,
    *,
    level: int,
    owned: set[str],
) -> UpgradeOfferResponse:
    reason: str | None = None
    if level < definition.min_level:
        reason = f"Requires level {definition.min_level}."
    elif definition.prerequisite_key and definition.prerequisite_key not in owned:
        reason = f"Requires {definition.prerequisite_key}."
    return UpgradeOfferResponse(
        key=definition.key,
        name=definition.name,
        tier=definition.tier,
        cost_cash=definition.cost_cash,
        yield_bonus=definition.yield_bonus,
        min_level=definition.min_level,
        prerequisite_key=definition.prerequisite_key,
        locked=reason is not None,
        locked_reason=reason,
    )


async def economy_state(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    now: datetime | None = None,
) -> EconomyState:
    current_time = now or datetime.now(UTC)
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    if wallet is None or progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player economic state is incomplete.", status_code=500)

    contracts = (
        await session.scalars(
            select(PlayerContract)
            .where(PlayerContract.user_id == user_id)
            .order_by(PlayerContract.accepted_at.desc())
        )
    ).all()
    active_contracts = [
        response
        for contract in contracts
        if contract.status == "active"
        for response in [_contract_response(contract)]
        if response is not None
    ]
    focus = active_contracts[0] if active_contracts else (
        _contract_response(contracts[0]) if contracts else None
    )

    accepted_offer_ids = {contract.offer_id for contract in contracts}
    offers = [
        offer
        for offer in generate_contract_offers(
            user_id=user_id,
            level=progression.level,
            reputation=progression.reputation,
            now=current_time,
        )
        if offer.offer_id not in accepted_offer_ids
    ]

    owned_keys = await _owned_upgrade_keys(session, user_id)
    owned = set(owned_keys)
    upgrade_offers = [
        _upgrade_response(upgrade, level=progression.level, owned=owned)
        for upgrade in UPGRADES
        if upgrade.key not in owned
    ]

    bucket = offer_bucket_for_time(current_time)
    return EconomyState(
        cash=wallet.cash,
        contract_offers=offers,
        contract_refresh_at=refresh_at_for_bucket(bucket),
        active_contract=focus,
        active_contracts=active_contracts,
        upgrade_offers=upgrade_offers,
        owned_upgrade_keys=owned_keys,
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


async def _action_response(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    focus_contract: PlayerContract | None = None,
) -> EconomyActionResponse:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id)
    )
    if wallet is None or inventory is None or progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player economic state is incomplete.", status_code=500)

    active_models = (
        await session.scalars(
            select(PlayerContract)
            .where(PlayerContract.user_id == user_id)
            .where(PlayerContract.status == "active")
            .order_by(PlayerContract.accepted_at.desc())
        )
    ).all()
    active = [
        response
        for contract in active_models
        for response in [_contract_response(contract)]
        if response is not None
    ]
    focus = _contract_response(focus_contract) if focus_contract is not None else (
        active[0] if active else None
    )

    return EconomyActionResponse(
        cash=wallet.cash,
        reputation=progression.reputation,
        level=progression.level,
        inventory=await inventory_responses(session, inventory.id),
        inventory_lots=await inventory_lot_responses(session, inventory.id),
        active_contract=focus,
        active_contracts=active,
        owned_upgrade_keys=await _owned_upgrade_keys(session, user_id),
    )


def _definition_for_item(item_key: str) -> tuple[str, ...]:
    prefix = "starter_crop."
    if not item_key.startswith(prefix):
        return ()
    variety = STARTER_VARIETY_BY_KEY.get(item_key.removeprefix(prefix))
    return variety.traits if variety is not None else ()


async def _consume_inventory(
    session: AsyncSession,
    *,
    inventory: InventoryContainer,
    item_key: str,
    quantity: int,
    required_quality: str | None,
) -> None:
    item = await session.scalar(
        select(InventoryItem)
        .where(InventoryItem.inventory_container_id == inventory.id)
        .where(InventoryItem.item_key == item_key)
        .with_for_update()
    )
    if item is None or item.quantity < quantity:
        raise AppError(
            "CONTRACT_INVENTORY_INSUFFICIENT",
            "Not enough inventory to complete this contract.",
            status_code=409,
            details={"required_quantity": quantity},
        )

    query = (
        select(InventoryLot)
        .where(InventoryLot.inventory_container_id == inventory.id)
        .where(InventoryLot.item_key == item_key)
        .where(InventoryLot.quantity > 0)
        .order_by(InventoryLot.quality.desc())
        .with_for_update()
    )
    if required_quality is not None:
        query = query.where(InventoryLot.quality == required_quality)

    lots = list((await session.scalars(query)).all())
    if sum(lot.quantity for lot in lots) < quantity:
        raise AppError(
            "CONTRACT_QUALITY_INSUFFICIENT",
            "Not enough inventory of the required quality.",
            status_code=409,
            details={"required_quantity": quantity, "required_quality": required_quality},
        )

    remaining = quantity
    for lot in lots:
        consumed = min(lot.quantity, remaining)
        lot.quantity -= consumed
        remaining -= consumed
        if remaining == 0:
            break
    item.quantity -= quantity


async def accept_offer(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    offer_id: str,
    request_id: str | None,
    now: datetime | None = None,
) -> PlayerContractResponse:
    current_time = now or datetime.now(UTC)
    progression = await _progression_for_update(session, user_id)
    current_offers = generate_contract_offers(
        user_id=user_id,
        level=progression.level,
        reputation=progression.reputation,
        now=current_time,
    )
    offer = next((item for item in current_offers if item.offer_id == offer_id), None)
    if offer is None:
        raise AppError("CONTRACT_OFFER_EXPIRED", "Contract offer is not current.", status_code=409)
    if offer.locked:
        raise AppError("CONTRACT_OFFER_LOCKED", "Contract offer is locked.", status_code=403)

    active_count = await session.scalar(
        select(func.count())
        .select_from(PlayerContract)
        .where(PlayerContract.user_id == user_id)
        .where(PlayerContract.status == "active")
    )
    if active_count is not None and active_count >= MAX_ACTIVE_CONTRACTS:
        raise AppError(
            "CONTRACT_ACTIVE_LIMIT",
            "Maximum active contract limit reached.",
            status_code=409,
        )

    existing = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.user_id == user_id)
        .where(PlayerContract.offer_id == offer.offer_id)
    )
    if existing is not None:
        response = _contract_response(existing)
        if response is None:
            raise AppError("CONTRACT_STATE_INVALID", "Contract state is invalid.", status_code=500)
        return response

    definition = CONTRACT_BY_KEY[offer.key]
    contract = PlayerContract(
        user_id=user_id,
        offer_id=offer.offer_id,
        offer_bucket=offer.offer_bucket,
        contract_key=definition.key,
        archetype=definition.archetype,
        config_version=ECONOMY_CONFIG_VERSION,
        item_key=definition.item_key,
        required_quantity=definition.required_quantity,
        required_quality=definition.required_quality,
        required_trait=definition.required_trait,
        reward_cash=definition.reward_cash,
        reward_reputation=definition.reward_reputation,
        status="active",
        accepted_at=current_time,
    )
    session.add(contract)
    await append_audit_event(
        session,
        event_type="economy.contract_accepted",
        actor_type="user",
        actor_id=str(user_id),
        target_type="contract_offer",
        target_id=offer.offer_id,
        request_id=request_id,
        payload={"contract_key": definition.key, "offer_bucket": offer.offer_bucket},
    )
    await session.commit()
    response = _contract_response(contract)
    if response is None:
        raise AppError("CONTRACT_STATE_INVALID", "Contract state is invalid.", status_code=500)
    return response


async def accept_contract(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    contract_key: str,
    request_id: str | None,
) -> PlayerContractResponse:
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)
    offers = generate_contract_offers(
        user_id=user_id,
        level=progression.level,
        reputation=progression.reputation,
        now=datetime.now(UTC),
    )
    offer = next((item for item in offers if item.key == contract_key), None)
    if offer is None:
        raise AppError("CONTRACT_NOT_FOUND", "Contract offer not found.", status_code=404)
    return await accept_offer(
        session,
        user_id=user_id,
        offer_id=offer.offer_id,
        request_id=request_id,
    )


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
        contract = await session.get(PlayerContract, contract_id)
        return await _action_response(session, user_id, focus_contract=contract)

    contract = await session.scalar(
        select(PlayerContract)
        .where(PlayerContract.id == contract_id)
        .where(PlayerContract.user_id == user_id)
        .with_for_update()
    )
    if contract is None:
        raise AppError("CONTRACT_NOT_FOUND", "Contract not found.", status_code=404)

    if await _check_idempotency(
        session,
        user_id=user_id,
        idempotency_key=idempotency_key,
        operation="contract.complete",
        reference_id=reference_id,
    ):
        return await _action_response(session, user_id, focus_contract=contract)

    if contract.status != "active":
        raise AppError("CONTRACT_ALREADY_COMPLETED", "Contract is already completed.", status_code=409)

    if contract.required_trait is not None:
        traits = _definition_for_item(contract.item_key)
        if contract.required_trait not in traits:
            raise AppError(
                "CONTRACT_TRAIT_MISMATCH",
                "Inventory does not satisfy the contract trait requirement.",
                status_code=409,
            )

    inventory = await _inventory_for_update(session, user_id)
    await _consume_inventory(
        session,
        inventory=inventory,
        item_key=contract.item_key,
        quantity=contract.required_quantity,
        required_quality=contract.required_quality,
    )

    wallet = await _wallet_for_update(session, user_id)
    progression = await _progression_for_update(session, user_id)
    before = wallet.cash
    after = before + contract.reward_cash
    wallet.cash = after
    progression.reputation += contract.reward_reputation
    contract.status = "completed"
    contract.completed_at = datetime.now(UTC)

    transaction_id = uuid.uuid4()
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=contract.reward_cash,
            source_or_sink="contract_reward",
            reference_type="contract",
            reference_id=str(contract.id),
            config_version=contract.config_version,
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
        payload={
            "cash_reward": contract.reward_cash,
            "reputation_reward": contract.reward_reputation,
            "transaction_id": str(transaction_id),
        },
    )
    await session.commit()
    return await _action_response(session, user_id, focus_contract=contract)


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

    wallet = await _wallet_for_update(session, user_id)
    progression = await _progression_for_update(session, user_id)

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

    owned = set(await _owned_upgrade_keys(session, user_id))
    if progression.level < definition.min_level:
        raise AppError(
            "UPGRADE_LEVEL_LOCKED",
            "Upgrade is locked by player level.",
            status_code=403,
            details={"required_level": definition.min_level},
        )
    if definition.prerequisite_key and definition.prerequisite_key not in owned:
        raise AppError(
            "UPGRADE_PREREQUISITE_LOCKED",
            "Upgrade prerequisite is not owned.",
            status_code=403,
            details={"prerequisite_key": definition.prerequisite_key},
        )
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
    session.add(PlayerUpgrade(user_id=user_id, upgrade_key=upgrade_key))

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
        payload={
            "cash_cost": definition.cost_cash,
            "tier": definition.tier,
            "transaction_id": str(transaction_id),
        },
    )
    await session.commit()
    return await _action_response(session, user_id)
