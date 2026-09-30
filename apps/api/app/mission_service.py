from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    EconomyLedger,
    MissionEventReceipt,
    MissionPoolAssignment,
    PlayerMission,
    PlayerVarietyMastery,
    Progression,
    Wallet,
)
from app.errors import AppError
from app.game_data.mission_catalog import (
    CONTACTS,
    MISSION_BY_KEY,
    MISSION_CONFIG_VERSION,
    MISSIONS,
    cosmetic_keys_for_variety,
    daily_period_key,
    daily_pool_keys,
    mastery_tier,
    next_mastery_threshold,
    weekly_period_key,
    weekly_pool_keys,
)
from app.game_data.production_catalog import STARTER_VARIETY_BY_KEY
from app.game_data.progression_catalog import awarded_skill_points, level_for_xp
from app.schemas import (
    ContactResponse,
    MissionRewardResponse,
    PlayerMissionResponse,
    VarietyMasteryResponse,
)


@dataclass(frozen=True)
class MetaState:
    contacts: list[ContactResponse]
    missions: list[PlayerMissionResponse]
    daily_mission_keys: list[str]
    weekly_mission_keys: list[str]
    mastery: list[VarietyMasteryResponse]
    unlocked_cosmetic_keys: list[str]


async def bootstrap_missions(session: AsyncSession, user_id: uuid.UUID) -> int:
    existing = (
        await session.scalars(
            select(PlayerMission)
            .where(PlayerMission.user_id == user_id)
            .order_by(PlayerMission.created_at, PlayerMission.mission_key)
        )
    ).all()
    by_key = {item.mission_key: item for item in existing}
    created = 0

    for definition in MISSIONS:
        if definition.key in by_key:
            continue
        model = PlayerMission(
            user_id=user_id,
            mission_key=definition.key,
            status="locked",
            progress=0,
        )
        session.add(model)
        by_key[definition.key] = model
        created += 1

    if created:
        await session.flush()

    if not any(item.status == "active" for item in by_key.values()):
        for definition in MISSIONS:
            model = by_key[definition.key]
            if model.status != "completed":
                model.status = "active"
                break

    return created


async def _persist_pool_assignments(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    period_type: str,
    period_key: str,
    mission_keys: list[str],
) -> list[str]:
    for slot_index, mission_key in enumerate(mission_keys):
        stmt = (
            insert(MissionPoolAssignment)
            .values(
                id=uuid.uuid4(),
                user_id=user_id,
                period_type=period_type,
                period_key=period_key,
                slot_index=slot_index,
                mission_key=mission_key,
                config_version=MISSION_CONFIG_VERSION,
            )
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)

    assignments = (
        await session.scalars(
            select(MissionPoolAssignment)
            .where(MissionPoolAssignment.user_id == user_id)
            .where(MissionPoolAssignment.period_type == period_type)
            .where(MissionPoolAssignment.period_key == period_key)
            .order_by(MissionPoolAssignment.slot_index)
        )
    ).all()
    return [item.mission_key for item in assignments]


async def _award_mission_reward(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    mission: PlayerMission,
    request_id: str | None,
) -> None:
    definition = MISSION_BY_KEY[mission.mission_key]
    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    wallet = await session.scalar(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    )
    if progression is None or wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Mission reward state is incomplete.", status_code=500)

    previous_level = progression.level
    previous_points = awarded_skill_points(previous_level)
    progression.xp += definition.reward_xp
    progression.reputation += definition.reward_reputation
    progression.level = level_for_xp(progression.xp)
    current_points = awarded_skill_points(progression.level)
    if current_points > previous_points:
        progression.skill_points_unspent += current_points - previous_points

    transaction_id: uuid.UUID | None = None
    if definition.reward_cash:
        before = wallet.cash
        wallet.cash += definition.reward_cash
        transaction_id = uuid.uuid4()
        session.add(
            EconomyLedger(
                transaction_id=transaction_id,
                user_id=user_id,
                currency="cash",
                amount=definition.reward_cash,
                source_or_sink="mission_reward",
                reference_type="mission",
                reference_id=definition.key,
                config_version=MISSION_CONFIG_VERSION,
                balance_before=before,
                balance_after=wallet.cash,
            )
        )

    mission.rewarded_at = datetime.now(UTC)
    await append_audit_event(
        session,
        event_type="meta.mission_completed",
        actor_type="user",
        actor_id=str(user_id),
        target_type="mission",
        target_id=definition.key,
        request_id=request_id,
        payload={
            "reward_cash": definition.reward_cash,
            "reward_xp": definition.reward_xp,
            "reward_reputation": definition.reward_reputation,
            "transaction_id": str(transaction_id) if transaction_id else None,
        },
    )


async def _activate_next_mission(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    sequence: int,
) -> None:
    next_definition = next((item for item in MISSIONS if item.sequence == sequence + 1), None)
    if next_definition is None:
        return
    next_model = await session.scalar(
        select(PlayerMission)
        .where(PlayerMission.user_id == user_id)
        .where(PlayerMission.mission_key == next_definition.key)
        .with_for_update()
    )
    if next_model is not None and next_model.status == "locked":
        next_model.status = "active"


def _objective_increment(
    *,
    objective_type: str,
    objective_key: str | None,
    event_type: str,
    amount: int,
    cash_earned: int,
    upgrade_key: str | None,
    variety_key: str | None,
) -> int:
    if (
        objective_key is not None
        and objective_type in {"plant", "harvest"}
        and objective_key != variety_key
    ):
        return 0
    if objective_type == "cash_earned":
        return cash_earned if event_type == "contract_complete" else 0
    if objective_type == "upgrade_owned":
        if event_type != "upgrade_owned":
            return 0
        if objective_key is not None and objective_key != upgrade_key:
            return 0
        return 1
    return amount if objective_type == event_type else 0


async def _increment_mastery(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    variety_key: str,
    harvest_quantity: int = 0,
    contract_quantity: int = 0,
) -> None:
    if variety_key not in STARTER_VARIETY_BY_KEY:
        return
    mastery = await session.scalar(
        select(PlayerVarietyMastery)
        .where(PlayerVarietyMastery.user_id == user_id)
        .where(PlayerVarietyMastery.variety_key == variety_key)
        .with_for_update()
    )
    if mastery is None:
        mastery = PlayerVarietyMastery(
            user_id=user_id,
            variety_key=variety_key,
            harvest_quantity=0,
            contract_quantity=0,
        )
        session.add(mastery)
        await session.flush()
    mastery.harvest_quantity += max(0, harvest_quantity)
    mastery.contract_quantity += max(0, contract_quantity)


async def record_domain_event(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    event_key: str,
    event_type: str,
    amount: int = 1,
    cash_earned: int = 0,
    variety_key: str | None = None,
    mastery_quantity: int = 0,
    item_key: str | None = None,
    contract_quantity: int = 0,
    upgrade_key: str | None = None,
    request_id: str | None = None,
) -> bool:
    receipt_stmt = (
        insert(MissionEventReceipt)
        .values(
            id=uuid.uuid4(),
            user_id=user_id,
            event_key=event_key,
            event_type=event_type,
        )
        .on_conflict_do_nothing(index_elements=["user_id", "event_key"])
        .returning(MissionEventReceipt.id)
    )
    receipt_id = (await session.execute(receipt_stmt)).scalar_one_or_none()
    if receipt_id is None:
        return False

    await bootstrap_missions(session, user_id)
    active_at_start = list(
        (
            await session.scalars(
                select(PlayerMission)
                .where(PlayerMission.user_id == user_id)
                .where(PlayerMission.status == "active")
                .with_for_update()
            )
        ).all()
    )

    now = datetime.now(UTC)
    for mission in active_at_start:
        definition = MISSION_BY_KEY.get(mission.mission_key)
        if definition is None:
            continue
        increment = _objective_increment(
            objective_type=definition.objective_type,
            objective_key=definition.objective_key,
            event_type=event_type,
            amount=amount,
            cash_earned=cash_earned,
            upgrade_key=upgrade_key,
            variety_key=variety_key,
        )
        if increment <= 0:
            continue
        mission.progress = min(definition.target, mission.progress + increment)
        if mission.progress >= definition.target and mission.status == "active":
            mission.status = "completed"
            mission.completed_at = now
            await _award_mission_reward(
                session,
                user_id=user_id,
                mission=mission,
                request_id=request_id,
            )
            await _activate_next_mission(
                session,
                user_id=user_id,
                sequence=definition.sequence,
            )

    if event_type == "harvest" and variety_key and mastery_quantity > 0:
        await _increment_mastery(
            session,
            user_id=user_id,
            variety_key=variety_key,
            harvest_quantity=mastery_quantity,
        )
    elif event_type == "contract_complete" and item_key and contract_quantity > 0:
        prefix = "starter_crop."
        if item_key.startswith(prefix):
            await _increment_mastery(
                session,
                user_id=user_id,
                variety_key=item_key.removeprefix(prefix),
                contract_quantity=contract_quantity,
            )
    return True


def _mission_response(model: PlayerMission) -> PlayerMissionResponse:
    definition = MISSION_BY_KEY[model.mission_key]
    return PlayerMissionResponse(
        key=definition.key,
        sequence=definition.sequence,
        contact_key=definition.contact_key,
        arc_key=definition.arc_key,
        arc_title=definition.arc_title,
        title=definition.title,
        description=definition.description,
        objective_type=definition.objective_type,
        objective_key=definition.objective_key,
        target=definition.target,
        progress=model.progress,
        status=model.status,
        reward=MissionRewardResponse(
            cash=definition.reward_cash,
            xp=definition.reward_xp,
            reputation=definition.reward_reputation,
        ),
        inbox_message=definition.inbox_message,
        completed_at=model.completed_at,
    )


def _mastery_response(model: PlayerVarietyMastery) -> VarietyMasteryResponse:
    variety = STARTER_VARIETY_BY_KEY.get(model.variety_key)
    points = model.harvest_quantity + model.contract_quantity
    cosmetics = cosmetic_keys_for_variety(model.variety_key, points)
    return VarietyMasteryResponse(
        variety_key=model.variety_key,
        variety_name=variety.name if variety else model.variety_key,
        harvest_quantity=model.harvest_quantity,
        contract_quantity=model.contract_quantity,
        points=points,
        tier=mastery_tier(points),
        next_threshold=next_mastery_threshold(points),
        unlocked_cosmetic_keys=cosmetics,
    )


async def meta_state(
    session: AsyncSession,
    user_id: uuid.UUID,
    *,
    now: datetime | None = None,
    persist_bootstrap: bool = False,
) -> MetaState:
    created = await bootstrap_missions(session, user_id)
    if created and persist_bootstrap:
        await session.commit()

    mission_models = (
        await session.scalars(select(PlayerMission).where(PlayerMission.user_id == user_id))
    ).all()
    mission_models = sorted(
        mission_models,
        key=lambda item: MISSION_BY_KEY[item.mission_key].sequence,
    )
    mastery_models = (
        await session.scalars(
            select(PlayerVarietyMastery)
            .where(PlayerVarietyMastery.user_id == user_id)
            .order_by(PlayerVarietyMastery.variety_key)
        )
    ).all()

    current_time = now or datetime.now(UTC)
    day = current_time.date()
    daily_keys = await _persist_pool_assignments(
        session,
        user_id=user_id,
        period_type="daily",
        period_key=daily_period_key(day),
        mission_keys=daily_pool_keys(user_id, day),
    )
    weekly_keys = await _persist_pool_assignments(
        session,
        user_id=user_id,
        period_type="weekly",
        period_key=weekly_period_key(day),
        mission_keys=weekly_pool_keys(user_id, day),
    )
    if persist_bootstrap:
        await session.commit()

    mastery = [_mastery_response(item) for item in mastery_models]
    cosmetics = sorted(
        {
            cosmetic
            for item in mastery
            for cosmetic in item.unlocked_cosmetic_keys
        }
    )
    return MetaState(
        contacts=[
            ContactResponse(
                key=item.key,
                name=item.name,
                role=item.role,
                tone=item.tone,
                intro_message=item.intro_message,
            )
            for item in CONTACTS
        ],
        missions=[_mission_response(item) for item in mission_models],
        daily_mission_keys=daily_keys,
        weekly_mission_keys=weekly_keys,
        mastery=mastery,
        unlocked_cosmetic_keys=cosmetics,
    )
