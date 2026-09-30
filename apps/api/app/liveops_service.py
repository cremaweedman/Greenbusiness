from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    AnalyticsEvent,
    AppMeta,
    EconomyLedger,
    LiveOpsConfigVersion,
    PlayerProfile,
    Progression,
    User,
    Wallet,
)
from app.errors import AppError
from app.schemas import (
    AdminCashMutationResponse,
    AdminLedgerEntryResponse,
    AdminPlayerLookupResponse,
    AnalyticsEventResponse,
    CoreFunnelResponse,
    CoreLoopDashboardResponse,
    EconomyDashboardResponse,
    FunnelStepResponse,
    LiveOpsConfigPayload,
    LiveOpsConfigResponse,
    WalletDistributionBucketResponse,
)

ACTIVE_CONFIG_META_KEY = "liveops.active_config_version"
ANALYTICS_SECRET_KEYS = {
    "authorization",
    "cookie",
    "email",
    "jwt",
    "password",
    "refresh_token",
    "token",
}
CORE_FUNNEL_EVENTS = [
    "auth.user_registered",
    "auth.login",
    "production.crop_planted",
    "production.crop_cared",
    "production.crop_harvested",
    "economy.contract_accepted",
    "economy.contract_completed",
    "economy.upgrade_purchased",
    "meta.mission_completed",
]
DEFAULT_CONFIG = LiveOpsConfigPayload(
    feature_flags={
        "production": True,
        "contracts": True,
        "upgrades": True,
        "missions": True,
    },
    kill_switches={
        "production": False,
        "contracts": False,
        "upgrades": False,
        "missions": False,
    },
    contract_multipliers={"default_cash": 1.0, "default_reputation": 1.0},
    event_windows={},
    notification_copy={},
    experiments={},
)
WALLET_BUCKETS = (
    ("0", 0, 0),
    ("1-499", 1, 499),
    ("500-999", 500, 999),
    ("1000-4999", 1000, 4999),
    ("5000+", 5000, None),
)


def _config_response(model: LiveOpsConfigVersion) -> LiveOpsConfigResponse:
    return LiveOpsConfigResponse(
        version=model.version,
        config=LiveOpsConfigPayload.model_validate(model.config),
        created_by=model.created_by,
        restored_from_version=model.restored_from_version,
        created_at=model.created_at,
    )


def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in ANALYTICS_SECRET_KEYS:
                continue
            clean[key_text] = _sanitize_payload(item)
        return clean
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, str | int | float | bool) or value is None:
        return value
    return str(value)


def analytics_category(event_name: str) -> str:
    if "." in event_name:
        return event_name.split(".", 1)[0]
    if "_" in event_name:
        return event_name.split("_", 1)[0]
    return "system"


async def record_analytics_event(
    session: AsyncSession,
    *,
    event_name: str,
    user_id: uuid.UUID | None = None,
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> AnalyticsEvent:
    event = AnalyticsEvent(
        user_id=user_id,
        event_name=event_name,
        category=analytics_category(event_name),
        payload=_sanitize_payload(payload or {}),
        request_id=request_id,
    )
    session.add(event)
    await session.flush()
    return event


async def active_config(session: AsyncSession) -> LiveOpsConfigResponse:
    active_meta = await session.scalar(
        select(AppMeta).where(AppMeta.key == ACTIVE_CONFIG_META_KEY)
    )
    if active_meta is None:
        return LiveOpsConfigResponse(
            version=0,
            config=DEFAULT_CONFIG,
            created_by="system-default",
            restored_from_version=None,
            created_at=await _database_now(session),
        )
    model = await session.scalar(
        select(LiveOpsConfigVersion).where(LiveOpsConfigVersion.version == int(active_meta.value))
    )
    if model is None:
        raise AppError("LIVEOPS_CONFIG_MISSING", "Active LiveOps config is missing.", status_code=500)
    return _config_response(model)


async def list_config_versions(
    session: AsyncSession,
    *,
    limit: int = 50,
) -> list[LiveOpsConfigResponse]:
    rows = (
        await session.scalars(
            select(LiveOpsConfigVersion)
            .order_by(desc(LiveOpsConfigVersion.version))
            .limit(max(1, min(limit, 200)))
        )
    ).all()
    return [_config_response(row) for row in rows]


async def _database_now(session: AsyncSession):
    return (await session.execute(select(func.now()))).scalar_one()


async def _next_config_version(session: AsyncSession) -> int:
    value = await session.scalar(select(func.max(LiveOpsConfigVersion.version)))
    return int(value or 0) + 1


async def _set_active_version(session: AsyncSession, version: int) -> None:
    active_meta = await session.scalar(
        select(AppMeta).where(AppMeta.key == ACTIVE_CONFIG_META_KEY).with_for_update()
    )
    if active_meta is None:
        session.add(AppMeta(key=ACTIVE_CONFIG_META_KEY, value=str(version)))
    else:
        active_meta.value = str(version)


async def publish_config(
    session: AsyncSession,
    *,
    config: LiveOpsConfigPayload,
    admin_actor_id: str,
    request_id: str | None,
) -> LiveOpsConfigResponse:
    version = await _next_config_version(session)
    model = LiveOpsConfigVersion(
        version=version,
        config=config.model_dump(mode="json"),
        created_by=admin_actor_id,
    )
    session.add(model)
    await session.flush()
    await _set_active_version(session, version)
    await append_audit_event(
        session,
        event_type="admin.liveops_config_published",
        actor_type="admin",
        actor_id=admin_actor_id,
        target_type="liveops_config",
        target_id=str(version),
        request_id=request_id,
        payload={"version": version},
    )
    await record_analytics_event(
        session,
        event_name="liveops.config_published",
        payload={"version": version},
        request_id=request_id,
    )
    await session.commit()
    return _config_response(model)


async def rollback_config(
    session: AsyncSession,
    *,
    source_version: int,
    admin_actor_id: str,
    request_id: str | None,
) -> LiveOpsConfigResponse:
    source = await session.scalar(
        select(LiveOpsConfigVersion).where(LiveOpsConfigVersion.version == source_version)
    )
    if source is None:
        raise AppError("LIVEOPS_CONFIG_NOT_FOUND", "Config version was not found.", status_code=404)
    version = await _next_config_version(session)
    restored = LiveOpsConfigVersion(
        version=version,
        config=source.config,
        created_by=admin_actor_id,
        restored_from_version=source.version,
    )
    session.add(restored)
    await session.flush()
    await _set_active_version(session, version)
    await append_audit_event(
        session,
        event_type="admin.liveops_config_rolled_back",
        actor_type="admin",
        actor_id=admin_actor_id,
        target_type="liveops_config",
        target_id=str(version),
        request_id=request_id,
        payload={"version": version, "restored_from_version": source.version},
    )
    await record_analytics_event(
        session,
        event_name="liveops.config_rolled_back",
        payload={"version": version, "restored_from_version": source.version},
        request_id=request_id,
    )
    await session.commit()
    return _config_response(restored)


async def require_feature_enabled(session: AsyncSession, feature_key: str) -> None:
    config = (await active_config(session)).config
    if config.kill_switches.get(feature_key, False) or not config.feature_flags.get(feature_key, True):
        raise AppError(
            "FEATURE_DISABLED",
            f"{feature_key} is currently disabled by LiveOps config.",
            status_code=503,
        )


async def contract_reward_multipliers(session: AsyncSession) -> tuple[float, float, int]:
    config = await active_config(session)
    cash = config.config.contract_multipliers.get("default_cash", 1.0)
    reputation = config.config.contract_multipliers.get("default_reputation", 1.0)
    return max(0.0, cash), max(0.0, reputation), config.version


def apply_contract_multiplier(value: int, multiplier: float) -> int:
    return max(0, round(value * multiplier))


def liveops_config_version_label(version: int) -> str:
    return f"liveops_{version}" if version > 0 else "liveops_default"


async def economy_dashboard(session: AsyncSession) -> EconomyDashboardResponse:
    minted = await session.scalar(
        select(func.coalesce(func.sum(EconomyLedger.amount), 0)).where(EconomyLedger.amount > 0)
    )
    burned = await session.scalar(
        select(func.coalesce(func.sum(EconomyLedger.amount), 0)).where(EconomyLedger.amount < 0)
    )
    wallet_count = await session.scalar(select(func.count()).select_from(Wallet))
    total_wallet_cash = await session.scalar(select(func.coalesce(func.sum(Wallet.cash), 0)))
    min_wallet_cash = await session.scalar(select(func.coalesce(func.min(Wallet.cash), 0)))
    max_wallet_cash = await session.scalar(select(func.coalesce(func.max(Wallet.cash), 0)))
    distribution: list[WalletDistributionBucketResponse] = []
    for label, min_cash, max_cash in WALLET_BUCKETS:
        query = select(func.count()).select_from(Wallet).where(Wallet.cash >= min_cash)
        if max_cash is not None:
            query = query.where(Wallet.cash <= max_cash)
        count = await session.scalar(query)
        distribution.append(
            WalletDistributionBucketResponse(
                label=label,
                min_cash=min_cash,
                max_cash=max_cash,
                wallet_count=int(count or 0),
            )
        )
    return EconomyDashboardResponse(
        currency="cash",
        minted=int(minted or 0),
        burned=abs(int(burned or 0)),
        wallet_count=int(wallet_count or 0),
        total_wallet_cash=int(total_wallet_cash or 0),
        min_wallet_cash=int(min_wallet_cash or 0),
        max_wallet_cash=int(max_wallet_cash or 0),
        wallet_distribution=distribution,
    )


async def core_funnel(session: AsyncSession) -> CoreFunnelResponse:
    rows = (
        await session.execute(
            select(AnalyticsEvent.event_name, func.count(AnalyticsEvent.id))
            .where(AnalyticsEvent.event_name.in_(CORE_FUNNEL_EVENTS))
            .group_by(AnalyticsEvent.event_name)
        )
    ).all()
    counts = {event_name: int(count) for event_name, count in rows}
    return CoreFunnelResponse(
        steps=[
            FunnelStepResponse(event_name=event_name, count=counts.get(event_name, 0))
            for event_name in CORE_FUNNEL_EVENTS
        ]
    )


async def core_loop_dashboard(session: AsyncSession) -> CoreLoopDashboardResponse:
    event_names = [
        "auth.user_registered",
        "production.crop_planted",
        "production.crop_cared",
        "production.crop_harvested",
        "economy.contract_accepted",
        "economy.contract_completed",
        "economy.upgrade_purchased",
        "meta.mission_completed",
        "errors.api_request_failed",
    ]
    rows = (
        await session.execute(
            select(AnalyticsEvent.event_name, func.count(AnalyticsEvent.id))
            .where(AnalyticsEvent.event_name.in_(event_names))
            .group_by(AnalyticsEvent.event_name)
        )
    ).all()
    counts = {event_name: int(count) for event_name, count in rows}
    tutorial_started = await session.scalar(
        select(func.count()).select_from(PlayerProfile).where(PlayerProfile.tutorial_step > 0)
    )
    tutorial_completed = await session.scalar(
        select(func.count()).select_from(PlayerProfile).where(PlayerProfile.tutorial_completed.is_(True))
    )
    return CoreLoopDashboardResponse(
        tutorial_started=int(tutorial_started or 0),
        tutorial_completed=int(tutorial_completed or 0),
        registered=counts.get("auth.user_registered", 0),
        planted=counts.get("production.crop_planted", 0),
        cared=counts.get("production.crop_cared", 0),
        harvested=counts.get("production.crop_harvested", 0),
        contracts_accepted=counts.get("economy.contract_accepted", 0),
        contracts_completed=counts.get("economy.contract_completed", 0),
        upgrades_purchased=counts.get("economy.upgrade_purchased", 0),
        missions_completed=counts.get("meta.mission_completed", 0),
        failed_requests=counts.get("errors.api_request_failed", 0),
    )


async def recent_analytics_events(session: AsyncSession, *, limit: int = 50) -> list[AnalyticsEventResponse]:
    rows = (
        await session.scalars(
            select(AnalyticsEvent)
            .order_by(desc(AnalyticsEvent.created_at))
            .limit(max(1, min(limit, 200)))
        )
    ).all()
    return [
        AnalyticsEventResponse(
            id=row.id,
            user_id=row.user_id,
            event_name=row.event_name,
            category=row.category,
            payload=row.payload,
            request_id=row.request_id,
            created_at=row.created_at,
        )
        for row in rows
    ]


async def ledger_entries(
    session: AsyncSession,
    *,
    user_id: uuid.UUID | None = None,
    limit: int = 50,
) -> list[AdminLedgerEntryResponse]:
    query = select(EconomyLedger).order_by(desc(EconomyLedger.created_at))
    if user_id is not None:
        query = query.where(EconomyLedger.user_id == user_id)
    rows = (await session.scalars(query.limit(max(1, min(limit, 200))))).all()
    return [
        AdminLedgerEntryResponse(
            id=row.id,
            transaction_id=row.transaction_id,
            user_id=row.user_id,
            currency=row.currency,
            amount=row.amount,
            source_or_sink=row.source_or_sink,
            reference_type=row.reference_type,
            reference_id=row.reference_id,
            config_version=row.config_version,
            balance_before=row.balance_before,
            balance_after=row.balance_after,
            created_at=row.created_at,
        )
        for row in rows
    ]


async def admin_cash_mutation(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    amount: int,
    source_or_sink: str,
    admin_actor_id: str,
    reason: str,
    request_id: str | None,
) -> AdminCashMutationResponse:
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id).with_for_update())
    if wallet is None:
        raise AppError("ADMIN_PLAYER_WALLET_NOT_FOUND", "Player wallet was not found.", status_code=404)

    signed_amount = amount if source_or_sink == "admin_grant" else -amount
    before = wallet.cash
    after = before + signed_amount
    if after < 0:
        raise AppError(
            "ADMIN_CASH_REVOKE_EXCEEDS_BALANCE",
            "Cannot revoke more Cash than the player has.",
            status_code=409,
            details={"cash": before, "requested_revoke": amount},
        )
    wallet.cash = after
    transaction_id = uuid.uuid4()
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=signed_amount,
            source_or_sink=source_or_sink,
            reference_type="admin_adjustment",
            reference_id=request_id or str(transaction_id),
            config_version="admin_manual_v1",
            balance_before=before,
            balance_after=after,
        )
    )
    await append_audit_event(
        session,
        event_type=f"admin.cash_{'granted' if signed_amount > 0 else 'revoked'}",
        actor_type="admin",
        actor_id=admin_actor_id,
        target_type="user",
        target_id=str(user_id),
        request_id=request_id,
        payload={
            "amount": signed_amount,
            "balance_before": before,
            "balance_after": after,
            "reason": reason,
            "transaction_id": str(transaction_id),
        },
    )
    await record_analytics_event(
        session,
        event_name=f"admin.cash_{'granted' if signed_amount > 0 else 'revoked'}",
        user_id=user_id,
        payload={"amount": signed_amount, "balance_after": after},
        request_id=request_id,
    )
    await session.commit()
    return AdminCashMutationResponse(
        user_id=user_id,
        cash=after,
        cash_delta=signed_amount,
        transaction_id=transaction_id,
    )


async def admin_player_lookup(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
) -> AdminPlayerLookupResponse:
    user = await session.get(User, user_id)
    if user is None:
        raise AppError("ADMIN_PLAYER_NOT_FOUND", "Player was not found.", status_code=404)
    profile = await session.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    return AdminPlayerLookupResponse(
        user_id=user.id,
        email=user.email,
        status=user.status,
        display_name=profile.display_name if profile else None,
        cash=wallet.cash if wallet else None,
        level=progression.level if progression else None,
        reputation=progression.reputation if progression else None,
        tutorial_step=profile.tutorial_step if profile else None,
        tutorial_completed=profile.tutorial_completed if profile else None,
    )
