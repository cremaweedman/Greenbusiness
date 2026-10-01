from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    Business,
    EconomyLedger,
    EconomyRequest,
    PlayerDecoration,
    Progression,
    Room,
    RoomDecoration,
    Wallet,
)
from app.errors import AppError
from app.game_data.decoration_catalog import (
    DECORATION_BY_KEY,
    DECORATION_CONFIG_VERSION,
    DECORATIONS,
)
from app.liveops_service import record_analytics_event
from app.schemas import (
    DecorationEquipResponse,
    DecorationItemResponse,
    DecorationPurchaseResponse,
    DecorationStateResponse,
)


async def _context(session: AsyncSession, user_id: uuid.UUID):
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    business = await session.scalar(select(Business).where(Business.user_id == user_id))
    room = (
        await session.scalar(select(Room).where(Room.business_id == business.id))
        if business is not None
        else None
    )
    if wallet is None or progression is None or room is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Decoration state is incomplete.", status_code=500)
    return wallet, progression, room


async def decoration_state(session: AsyncSession, user_id: uuid.UUID) -> DecorationStateResponse:
    wallet, progression, room = await _context(session, user_id)
    owned = set(
        (
            await session.scalars(
                select(PlayerDecoration.decoration_key).where(PlayerDecoration.user_id == user_id)
            )
        ).all()
    )
    equipped_rows = (
        await session.scalars(
            select(RoomDecoration).where(RoomDecoration.room_id == room.id)
        )
    ).all()
    equipped = {row.decoration_key: row.slot_index for row in equipped_rows}
    return DecorationStateResponse(
        cash=wallet.cash,
        items=[
            DecorationItemResponse(
                key=item.key,
                name=item.name,
                category=item.category,
                cost_cash=item.cost_cash,
                min_level=item.min_level,
                owned=item.key in owned,
                equipped_slot=equipped.get(item.key),
                locked=progression.level < item.min_level,
            )
            for item in DECORATIONS
        ],
    )


async def purchase_decoration(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    decoration_key: str,
    idempotency_key: str,
    request_id: str | None,
) -> DecorationPurchaseResponse:
    definition = DECORATION_BY_KEY.get(decoration_key)
    if definition is None:
        raise AppError("DECORATION_NOT_FOUND", "Decoration was not found.", status_code=404)

    existing_request = await session.scalar(
        select(EconomyRequest).where(
            EconomyRequest.user_id == user_id,
            EconomyRequest.idempotency_key == idempotency_key,
        )
    )
    if existing_request is not None:
        if (
            existing_request.operation != "decoration.purchase"
            or existing_request.reference_id != decoration_key
        ):
            raise AppError("ECONOMY_IDEMPOTENCY_CONFLICT", "Idempotency key conflict.", status_code=409)
        state = await decoration_state(session, user_id)
        return DecorationPurchaseResponse(
            cash=state.cash,
            item=next(item for item in state.items if item.key == decoration_key),
        )

    wallet, progression, _room = await _context(session, user_id)
    wallet = await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    )
    if wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Wallet is missing.", status_code=500)
    owned = await session.scalar(
        select(PlayerDecoration).where(
            PlayerDecoration.user_id == user_id,
            PlayerDecoration.decoration_key == decoration_key,
        )
    )
    if owned is not None:
        raise AppError("DECORATION_ALREADY_OWNED", "Decoration is already owned.", status_code=409)
    if progression.level < definition.min_level:
        raise AppError(
            "DECORATION_LEVEL_LOCKED",
            "Decoration is locked by level.",
            status_code=403,
            details={"required_level": definition.min_level},
        )
    if wallet.cash < definition.cost_cash:
        raise AppError("ECONOMY_CASH_INSUFFICIENT", "Not enough Cash.", status_code=409)

    before = wallet.cash
    wallet.cash -= definition.cost_cash
    transaction_id = uuid.uuid4()
    session.add(PlayerDecoration(user_id=user_id, decoration_key=decoration_key))
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=-definition.cost_cash,
            source_or_sink="decoration_purchase",
            reference_type="decoration",
            reference_id=decoration_key,
            config_version=DECORATION_CONFIG_VERSION,
            balance_before=before,
            balance_after=wallet.cash,
        )
    )
    session.add(
        EconomyRequest(
            user_id=user_id,
            idempotency_key=idempotency_key,
            operation="decoration.purchase",
            reference_id=decoration_key,
        )
    )
    await append_audit_event(
        session,
        event_type="cosmetic.decoration_purchased",
        actor_type="user",
        actor_id=str(user_id),
        target_type="decoration",
        target_id=decoration_key,
        request_id=request_id,
        payload={"cash_cost": definition.cost_cash, "transaction_id": str(transaction_id)},
    )
    await record_analytics_event(
        session,
        event_name="cosmetic.decoration_purchased",
        user_id=user_id,
        payload={"decoration_key": decoration_key, "cash_cost": definition.cost_cash},
        request_id=request_id,
    )
    await session.commit()
    state = await decoration_state(session, user_id)
    return DecorationPurchaseResponse(
        cash=state.cash,
        item=next(item for item in state.items if item.key == decoration_key),
    )


async def equip_decoration(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    decoration_key: str,
    slot_index: int,
    request_id: str | None,
) -> DecorationEquipResponse:
    if decoration_key not in DECORATION_BY_KEY:
        raise AppError("DECORATION_NOT_FOUND", "Decoration was not found.", status_code=404)
    owned = await session.scalar(
        select(PlayerDecoration).where(
            PlayerDecoration.user_id == user_id,
            PlayerDecoration.decoration_key == decoration_key,
        )
    )
    if owned is None:
        raise AppError("DECORATION_NOT_OWNED", "Decoration must be purchased first.", status_code=403)
    _wallet, _progression, room = await _context(session, user_id)

    occupying = await session.scalar(
        select(RoomDecoration)
        .where(RoomDecoration.room_id == room.id, RoomDecoration.slot_index == slot_index)
        .with_for_update()
    )
    current = await session.scalar(
        select(RoomDecoration)
        .where(RoomDecoration.room_id == room.id, RoomDecoration.decoration_key == decoration_key)
        .with_for_update()
    )
    if occupying is not None and (current is None or occupying.id != current.id):
        await session.delete(occupying)
        await session.flush()
    if current is None:
        current = RoomDecoration(
            room_id=room.id,
            slot_index=slot_index,
            decoration_key=decoration_key,
        )
        session.add(current)
    else:
        current.slot_index = slot_index

    await record_analytics_event(
        session,
        event_name="cosmetic.decoration_equipped",
        user_id=user_id,
        payload={"decoration_key": decoration_key, "slot_index": slot_index},
        request_id=request_id,
    )
    await session.commit()
    return DecorationEquipResponse(decoration_key=decoration_key, slot_index=slot_index)
