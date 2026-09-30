from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.contracts_service import CASH_CURRENCY, cash_balance, cash_summary
from app.db.models import CurrencyLedgerEntry, PlayerUpgrade
from app.errors import AppError
from app.game_data.upgrades_catalog import (
    STARTER_UPGRADE_BY_KEY,
    STARTER_UPGRADES,
    STARTER_UPGRADES_CATALOG,
    StarterUpgrade,
)
from app.schemas import (
    UpgradeEffectsResponse,
    UpgradePurchaseResponse,
    UpgradeResponse,
)

UPGRADE_SOURCE = "upgrade_purchase"
UPGRADE_CONSTRAINT = "uq_player_upgrade_user_key"


async def _owned_upgrade_levels(session: AsyncSession, user_id: uuid.UUID) -> dict[str, int]:
    rows = await session.scalars(select(PlayerUpgrade).where(PlayerUpgrade.user_id == user_id))
    return {upgrade.upgrade_key: upgrade.level for upgrade in rows.all()}


def _upgrade_response(
    upgrade: StarterUpgrade,
    *,
    level: int,
    balance: int,
) -> UpgradeResponse:
    return UpgradeResponse(
        key=upgrade.key,
        name=upgrade.name,
        description=upgrade.description,
        cash_cost=upgrade.cash_cost,
        level=level,
        max_level=upgrade.max_level,
        effects=UpgradeEffectsResponse(yield_bonus=upgrade.effects.yield_bonus),
        can_purchase=level < upgrade.max_level and balance >= upgrade.cash_cost,
    )


async def upgrade_responses(session: AsyncSession, *, user_id: uuid.UUID) -> list[UpgradeResponse]:
    levels = await _owned_upgrade_levels(session, user_id)
    balance = await cash_balance(session, user_id)
    return [
        _upgrade_response(upgrade, level=levels.get(upgrade.key, 0), balance=balance)
        for upgrade in STARTER_UPGRADES
    ]


async def total_yield_bonus(session: AsyncSession, *, user_id: uuid.UUID) -> int:
    levels = await _owned_upgrade_levels(session, user_id)
    return sum(
        upgrade.effects.yield_bonus * levels.get(upgrade.key, 0)
        for upgrade in STARTER_UPGRADES
    )


def _is_duplicate_upgrade(exc: IntegrityError) -> bool:
    constraint_name = getattr(getattr(exc, "orig", None), "constraint_name", None)
    return constraint_name == UPGRADE_CONSTRAINT or UPGRADE_CONSTRAINT in str(exc.orig)


async def purchase_upgrade(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    upgrade_key: str,
    request_id: str | None,
) -> UpgradePurchaseResponse:
    upgrade = STARTER_UPGRADE_BY_KEY.get(upgrade_key)
    if upgrade is None:
        raise AppError("UPGRADE_NOT_FOUND", "Upgrade is not available.", status_code=404)

    existing = await session.scalar(
        select(PlayerUpgrade)
        .where(PlayerUpgrade.user_id == user_id)
        .where(PlayerUpgrade.upgrade_key == upgrade.key)
        .with_for_update()
    )
    if existing is not None and existing.level >= upgrade.max_level:
        raise AppError("UPGRADE_MAX_LEVEL", "Upgrade is already at max level.", status_code=409)

    balance_before = await cash_balance(session, user_id)
    if balance_before < upgrade.cash_cost:
        raise AppError(
            "UPGRADE_CASH_INSUFFICIENT",
            "Not enough Cash for this upgrade.",
            status_code=409,
            details={"required": upgrade.cash_cost, "available": balance_before},
        )

    now = datetime.now(UTC)
    next_level = 1 if existing is None else existing.level + 1
    balance_after = balance_before - upgrade.cash_cost

    if existing is None:
        session.add(
            PlayerUpgrade(
                user_id=user_id,
                upgrade_key=upgrade.key,
                level=next_level,
                purchased_at=now,
            )
        )
    else:
        existing.level = next_level
        existing.purchased_at = now

    ledger_entry = CurrencyLedgerEntry(
        user_id=user_id,
        currency=CASH_CURRENCY,
        source=UPGRADE_SOURCE,
        source_id=f"{upgrade.key}:{next_level}",
        amount=-upgrade.cash_cost,
        balance_before=balance_before,
        balance_after=balance_after,
        config_version=STARTER_UPGRADES_CATALOG.version,
    )
    session.add(ledger_entry)
    await append_audit_event(
        session,
        event_type="upgrades.upgrade_purchased",
        actor_type="user",
        actor_id=str(user_id),
        target_type="upgrade",
        target_id=upgrade.key,
        request_id=request_id,
        payload={
            "level": next_level,
            "cash_cost": upgrade.cash_cost,
            "balance_after": balance_after,
            "config_version": STARTER_UPGRADES_CATALOG.version,
        },
    )
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if _is_duplicate_upgrade(exc):
            raise AppError("UPGRADE_MAX_LEVEL", "Upgrade is already at max level.", status_code=409) from exc
        raise

    return UpgradePurchaseResponse(
        upgrade=_upgrade_response(upgrade, level=next_level, balance=balance_after),
        cash_balance=balance_after,
        cash_delta=-upgrade.cash_cost,
        economy_summary=await cash_summary(session, user_id=user_id),
    )
