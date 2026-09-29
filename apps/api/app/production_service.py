from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    Business,
    CropProduction,
    InventoryContainer,
    InventoryItem,
    PlayerProfile,
    PlayerUpgrade,
    ProductionSlot,
    Progression,
    Room,
)
from app.errors import AppError
from app.game_data.economy_catalog import STARTER_UPGRADE
from app.game_data.production_catalog import STARTER_VARIETIES, STARTER_VARIETY_BY_KEY
from app.schemas import (
    CropProductionResponse,
    HarvestResponse,
    InventoryItemResponse,
    ProductionSlotResponse,
    StarterVarietyResponse,
)

XP_PER_HARVEST_UNIT = 5
ACTIVE_SLOT_CONSTRAINT = "uq_crop_productions_active_slot"


def starter_variety_responses() -> list[StarterVarietyResponse]:
    return [
        StarterVarietyResponse(
            key=variety.key,
            name=variety.name,
            grow_seconds=variety.grow_seconds,
            base_yield=variety.base_yield,
        )
        for variety in STARTER_VARIETIES
    ]


def _now() -> datetime:
    return datetime.now(UTC)


def _is_active_slot_integrity_error(exc: IntegrityError) -> bool:
    constraint_name = getattr(getattr(exc, "orig", None), "constraint_name", None)
    return constraint_name == ACTIVE_SLOT_CONSTRAINT or ACTIVE_SLOT_CONSTRAINT in str(exc.orig)


def _display_name(item_key: str) -> str:
    prefix = "starter_crop."
    if item_key.startswith(prefix):
        variety = STARTER_VARIETY_BY_KEY.get(item_key.removeprefix(prefix))
        if variety is not None:
            return variety.name
    return item_key.replace("_", " ").replace(".", " ").title()


def _slot_status(crop: CropProduction | None, now: datetime) -> str:
    if crop is None:
        return "available"
    if crop.ready_at <= now:
        return "ready"
    return "planted"


def _crop_response(crop: CropProduction | None, now: datetime) -> CropProductionResponse | None:
    if crop is None:
        return None
    variety = STARTER_VARIETY_BY_KEY[crop.variety_key]
    return CropProductionResponse(
        id=crop.id,
        variety_key=crop.variety_key,
        variety_name=variety.name,
        planted_at=crop.planted_at,
        ready_at=crop.ready_at,
        cared_at=crop.cared_at,
        is_ready=crop.ready_at <= now,
    )


def slot_response(
    slot: ProductionSlot,
    crop: CropProduction | None,
    now: datetime | None = None,
) -> ProductionSlotResponse:
    current_time = now or _now()
    return ProductionSlotResponse(
        id=slot.id,
        slot_index=slot.slot_index,
        status=_slot_status(crop, current_time),
        crop=_crop_response(crop, current_time),
    )


async def inventory_responses(
    session: AsyncSession,
    inventory_container_id: uuid.UUID,
) -> list[InventoryItemResponse]:
    items = (
        await session.scalars(
            select(InventoryItem)
            .where(InventoryItem.inventory_container_id == inventory_container_id)
            .order_by(InventoryItem.item_key)
        )
    ).all()
    return [
        InventoryItemResponse(
            item_key=item.item_key,
            display_name=_display_name(item.item_key),
            quantity=item.quantity,
        )
        for item in items
    ]


async def get_active_crops_by_slot(
    session: AsyncSession,
    slot_ids: list[uuid.UUID],
) -> dict[uuid.UUID, CropProduction]:
    if not slot_ids:
        return {}
    crops = (
        await session.scalars(
            select(CropProduction)
            .where(CropProduction.slot_id.in_(slot_ids))
            .where(CropProduction.harvested_at.is_(None))
        )
    ).all()
    return {crop.slot_id: crop for crop in crops}


async def _get_owned_slot(
    session: AsyncSession,
    user_id: uuid.UUID,
    slot_id: uuid.UUID,
) -> ProductionSlot:
    slot = await session.scalar(
        select(ProductionSlot)
        .join(Room, ProductionSlot.room_id == Room.id)
        .join(Business, Room.business_id == Business.id)
        .where(ProductionSlot.id == slot_id)
        .where(Business.user_id == user_id)
        .with_for_update()
    )
    if slot is None:
        raise AppError("PRODUCTION_SLOT_NOT_FOUND", "Production slot not found.", status_code=404)
    return slot


async def _get_active_crop(session: AsyncSession, slot_id: uuid.UUID) -> CropProduction | None:
    return await session.scalar(
        select(CropProduction)
        .where(CropProduction.slot_id == slot_id)
        .where(CropProduction.harvested_at.is_(None))
        .with_for_update()
    )


async def _advance_tutorial(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    minimum_step: int,
    completed: bool = False,
) -> None:
    profile = await session.scalar(
        select(PlayerProfile).where(PlayerProfile.user_id == user_id).with_for_update()
    )
    if profile is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player profile is missing.", status_code=500)
    profile.tutorial_step = max(profile.tutorial_step, minimum_step)
    if completed:
        profile.tutorial_completed = True


async def plant_crop(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    slot_id: uuid.UUID,
    variety_key: str,
    request_id: str | None,
) -> ProductionSlotResponse:
    variety = STARTER_VARIETY_BY_KEY.get(variety_key)
    if variety is None:
        raise AppError(
            "PRODUCTION_VARIETY_INVALID",
            "Starter variety is not available.",
            status_code=400,
        )

    slot = await _get_owned_slot(session, user_id, slot_id)
    active_crop = await _get_active_crop(session, slot.id)
    if active_crop is not None:
        raise AppError("PRODUCTION_SLOT_OCCUPIED", "Production slot is already planted.", status_code=409)

    now = _now()
    crop = CropProduction(
        slot_id=slot.id,
        variety_key=variety.key,
        planted_at=now,
        ready_at=now + timedelta(seconds=variety.grow_seconds),
    )
    slot.status = "planted"
    session.add(crop)
    await _advance_tutorial(session, user_id, minimum_step=1)
    await append_audit_event(
        session,
        event_type="production.crop_planted",
        actor_type="user",
        actor_id=str(user_id),
        target_type="production_slot",
        target_id=str(slot.id),
        request_id=request_id,
        payload={"variety_key": variety.key, "ready_at": crop.ready_at.isoformat()},
    )
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if _is_active_slot_integrity_error(exc):
            raise AppError(
                "PRODUCTION_SLOT_OCCUPIED",
                "Production slot is already planted.",
                status_code=409,
            ) from exc
        raise
    return slot_response(slot, crop, now)


async def care_for_crop(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    slot_id: uuid.UUID,
    request_id: str | None,
) -> ProductionSlotResponse:
    slot = await _get_owned_slot(session, user_id, slot_id)
    crop = await _get_active_crop(session, slot.id)
    if crop is None:
        raise AppError("PRODUCTION_SLOT_EMPTY", "Production slot has no active crop.", status_code=409)
    if crop.cared_at is not None:
        raise AppError("PRODUCTION_ALREADY_CARED", "Crop has already received care.", status_code=409)

    now = _now()
    crop.cared_at = now
    await _advance_tutorial(session, user_id, minimum_step=2)
    await append_audit_event(
        session,
        event_type="production.crop_cared",
        actor_type="user",
        actor_id=str(user_id),
        target_type="crop_production",
        target_id=str(crop.id),
        request_id=request_id,
    )
    await session.commit()
    return slot_response(slot, crop, now)


async def harvest_crop(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    slot_id: uuid.UUID,
    request_id: str | None,
) -> HarvestResponse:
    slot = await _get_owned_slot(session, user_id, slot_id)
    crop = await _get_active_crop(session, slot.id)
    if crop is None:
        raise AppError("PRODUCTION_SLOT_EMPTY", "Production slot has no active crop.", status_code=409)

    now = _now()
    if crop.ready_at > now:
        raise AppError(
            "PRODUCTION_CROP_NOT_READY",
            "Crop is not ready for harvest.",
            status_code=409,
            details={"ready_at": crop.ready_at.isoformat()},
        )

    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id).with_for_update()
    )
    if inventory is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player inventory is missing.", status_code=500)
    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)

    variety = STARTER_VARIETY_BY_KEY[crop.variety_key]
    care_bonus = 1 if crop.cared_at is not None else 0
    has_yield_upgrade = (
        await session.scalar(
            select(PlayerUpgrade.id)
            .where(PlayerUpgrade.user_id == user_id)
            .where(PlayerUpgrade.upgrade_key == STARTER_UPGRADE.key)
        )
        is not None
    )
    upgrade_bonus = STARTER_UPGRADE.yield_bonus if has_yield_upgrade else 0
    quality = "cared" if crop.cared_at is not None else "standard"
    yield_quantity = variety.base_yield + care_bonus + upgrade_bonus
    xp_reward = yield_quantity * XP_PER_HARVEST_UNIT
    item_key = variety.item_key

    item = await session.scalar(
        select(InventoryItem)
        .where(InventoryItem.inventory_container_id == inventory.id)
        .where(InventoryItem.item_key == item_key)
        .with_for_update()
    )
    if item is None:
        item = InventoryItem(
            inventory_container_id=inventory.id,
            item_key=item_key,
            quantity=0,
        )
        session.add(item)
        await session.flush()

    item.quantity += yield_quantity
    crop.harvested_at = now
    crop.yield_quantity = yield_quantity
    crop.quality = quality
    slot.status = "available"
    progression.xp += xp_reward
    await _advance_tutorial(session, user_id, minimum_step=3, completed=True)

    await append_audit_event(
        session,
        event_type="production.crop_harvested",
        actor_type="user",
        actor_id=str(user_id),
        target_type="crop_production",
        target_id=str(crop.id),
        request_id=request_id,
        payload={
            "item_key": item_key,
            "yield_quantity": yield_quantity,
            "quality": quality,
            "xp_reward": xp_reward,
            "upgrade_bonus": upgrade_bonus,
        },
    )
    await session.commit()

    all_inventory = await inventory_responses(session, inventory.id)
    harvested_item = InventoryItemResponse(
        item_key=item.item_key,
        display_name=_display_name(item.item_key),
        quantity=item.quantity,
    )
    return HarvestResponse(
        slot=slot_response(slot, None, now),
        inventory=all_inventory,
        harvested_item=harvested_item,
        yield_quantity=yield_quantity,
        quality=quality,
        xp_reward=xp_reward,
    )
