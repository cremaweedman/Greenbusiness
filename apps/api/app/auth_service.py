from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.config import settings
from app.db.models import (
    AuthSession,
    Business,
    InventoryContainer,
    PlayerEntitlement,
    PlayerProfile,
    PlayerSkillBranch,
    PremiumWallet,
    ProductionSlot,
    Progression,
    Room,
    User,
)
from app.economy_service import bootstrap_wallet, economy_state
from app.errors import AppError
from app.game_data.progression_catalog import (
    SKILL_BRANCHES,
    SKILL_MAX_POINTS,
    next_level_xp,
    skill_branch_label,
    skill_next_tier_label,
    unlocked_keys,
)
from app.liveops_service import record_analytics_event
from app.mission_service import bootstrap_missions, meta_state
from app.production_service import (
    get_active_crops_by_slot,
    inventory_lot_responses,
    inventory_responses,
    slot_response,
    starter_variety_responses,
)
from app.schemas import PlayerResponse, SkillBranchResponse
from app.security import (
    create_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    normalize_email,
    verify_password,
)


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == normalize_email(email)))


async def _get_user(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def _bootstrap_player_account(
    session: AsyncSession,
    *,
    email: str,
    password_hash: str,
    display_name: str,
) -> tuple[User, PlayerProfile]:
    clean_display_name = display_name.strip() or "Creator"
    user = User(email=normalize_email(email), password_hash=password_hash)
    session.add(user)
    await session.flush()

    profile = PlayerProfile(user_id=user.id, display_name=clean_display_name)
    business = Business(user_id=user.id, name=f"{clean_display_name}'s GreenBusiness")
    progression = Progression(
        user_id=user.id,
        level=1,
        xp=0,
        reputation=0,
        skill_points_unspent=0,
    )
    inventory = InventoryContainer(user_id=user.id, kind="main")
    skill_branches = [
        PlayerSkillBranch(user_id=user.id, branch=branch_name, points=0)
        for branch_name in SKILL_BRANCHES
    ]

    session.add_all([profile, business, progression, inventory, *skill_branches])
    await session.flush()
    await bootstrap_wallet(session, user.id)
    await bootstrap_missions(session, user.id)

    room = Room(business_id=business.id, slug="starter-growroom", level=1)
    session.add(room)
    await session.flush()

    session.add_all(
        [
            ProductionSlot(room_id=room.id, slot_index=0, status="available"),
            ProductionSlot(room_id=room.id, slot_index=1, status="available"),
            ProductionSlot(room_id=room.id, slot_index=2, status="available"),
        ]
    )
    return user, profile


async def _issue_session(
    session: AsyncSession,
    *,
    user: User,
    event_type: str,
    request_id: str | None,
    analytics_event_name: str,
    analytics_payload: dict[str, object] | None = None,
) -> tuple[str, str]:
    refresh_token = new_refresh_token()
    auth_session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.refresh_ttl_seconds),
    )
    session.add(auth_session)
    await append_audit_event(
        session,
        event_type=event_type,
        actor_type="user",
        actor_id=str(user.id),
        target_type="user",
        target_id=str(user.id),
        request_id=request_id,
        payload=analytics_payload or {},
    )
    await record_analytics_event(
        session,
        event_name=analytics_event_name,
        user_id=user.id,
        payload=analytics_payload,
        request_id=request_id,
    )
    return create_access_token(user.id), refresh_token


async def register_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    display_name: str,
    request_id: str | None,
) -> tuple[User, str, str]:
    normalized = normalize_email(email)
    existing = await _get_user_by_email(session, normalized)
    if existing is not None:
        raise AppError(
            "AUTH_EMAIL_EXISTS",
            "An account with this email already exists.",
            status_code=409,
        )

    user, profile = await _bootstrap_player_account(
        session,
        email=normalized,
        password_hash=hash_password(password),
        display_name=display_name,
    )

    access_token, refresh_token = await _issue_session(
        session,
        user=user,
        event_type="auth.user_registered",
        request_id=request_id,
        analytics_event_name="auth.user_registered",
        analytics_payload={"tutorial_step": profile.tutorial_step},
    )

    await session.commit()
    return user, access_token, refresh_token


def _creator_access_allowed() -> bool:
    return settings.creator_access_enabled and settings.app_env.lower() in {
        "development",
        "local",
        "test",
    }


async def login_or_create_creator_user(
    session: AsyncSession,
    *,
    request_id: str | None,
) -> tuple[User, str, str]:
    if not _creator_access_allowed():
        raise AppError(
            "CREATOR_ACCESS_DISABLED",
            "Creator access is disabled outside local development.",
            status_code=404,
        )

    normalized = normalize_email(settings.creator_email)
    user = await _get_user_by_email(session, normalized)
    profile: PlayerProfile | None = None
    if user is None:
        user, profile = await _bootstrap_player_account(
            session,
            email=normalized,
            password_hash=hash_password(token_urlsafe(48)),
            display_name=settings.creator_display_name,
        )
        event_type = "auth.creator_created"
        analytics_event_name = "auth.creator_created"
    else:
        if user.status != "active":
            raise AppError("AUTH_ACCOUNT_INACTIVE", "Creator account is inactive.", status_code=403)
        event_type = "auth.creator_login"
        analytics_event_name = "auth.creator_login"

    access_token, refresh_token = await _issue_session(
        session,
        user=user,
        event_type=event_type,
        request_id=request_id,
        analytics_event_name=analytics_event_name,
        analytics_payload={"creator_access": True},
    )
    if profile is not None:
        await record_analytics_event(
            session,
            event_name="auth.user_registered",
            user_id=user.id,
            payload={"tutorial_step": profile.tutorial_step, "creator_access": True},
            request_id=request_id,
        )
    await session.commit()
    return user, access_token, refresh_token


async def login_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    request_id: str | None,
) -> tuple[User, str, str]:
    user = await _get_user_by_email(session, email)
    if user is None or not verify_password(user.password_hash, password):
        raise AppError(
            "AUTH_INVALID_CREDENTIALS",
            "Invalid email or password.",
            status_code=401,
        )
    if user.status != "active":
        raise AppError("AUTH_ACCOUNT_INACTIVE", "Account is inactive.", status_code=403)

    refresh_token = new_refresh_token()
    auth_session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.refresh_ttl_seconds),
    )
    session.add(auth_session)
    await append_audit_event(
        session,
        event_type="auth.login",
        actor_type="user",
        actor_id=str(user.id),
        request_id=request_id,
    )
    await record_analytics_event(
        session,
        event_name="auth.login",
        user_id=user.id,
        request_id=request_id,
    )
    await session.commit()
    return user, create_access_token(user.id), refresh_token


async def rotate_refresh_token(
    session: AsyncSession,
    *,
    refresh_token: str,
    request_id: str | None,
) -> tuple[User, str, str]:
    token_hash = hash_refresh_token(refresh_token)
    auth_session = await session.scalar(
        select(AuthSession).where(AuthSession.refresh_token_hash == token_hash).with_for_update()
    )
    now = datetime.now(UTC)
    if (
        auth_session is None
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= now
    ):
        raise AppError("AUTH_REFRESH_INVALID", "Refresh token is invalid.", status_code=401)

    user = await _get_user(session, auth_session.user_id)
    if user is None or user.status != "active":
        raise AppError("AUTH_REFRESH_INVALID", "Refresh token is invalid.", status_code=401)

    auth_session.revoked_at = now
    replacement = new_refresh_token()
    new_session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(replacement),
        expires_at=now + timedelta(seconds=settings.refresh_ttl_seconds),
        rotated_from_id=auth_session.id,
    )
    session.add(new_session)
    await append_audit_event(
        session,
        event_type="auth.refresh_rotated",
        actor_type="user",
        actor_id=str(user.id),
        target_type="auth_session",
        target_id=str(auth_session.id),
        request_id=request_id,
    )
    await session.commit()
    return user, create_access_token(user.id), replacement


async def revoke_refresh_token(
    session: AsyncSession,
    *,
    refresh_token: str | None,
    request_id: str | None,
) -> None:
    if not refresh_token:
        return
    auth_session = await session.scalar(
        select(AuthSession)
        .where(AuthSession.refresh_token_hash == hash_refresh_token(refresh_token))
        .with_for_update()
    )
    if auth_session is None or auth_session.revoked_at is not None:
        return

    auth_session.revoked_at = datetime.now(UTC)
    await append_audit_event(
        session,
        event_type="auth.logout",
        actor_type="user",
        actor_id=str(auth_session.user_id),
        target_type="auth_session",
        target_id=str(auth_session.id),
        request_id=request_id,
    )
    await session.commit()


async def get_player_state(session: AsyncSession, user_id: uuid.UUID) -> PlayerResponse:
    now = datetime.now(UTC)
    user = await session.get(User, user_id)
    if user is None:
        raise AppError("PLAYER_NOT_FOUND", "Player not found.", status_code=404)

    profile = await session.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    business = await session.scalar(select(Business).where(Business.user_id == user_id))
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    inventory = await session.scalar(
        select(InventoryContainer).where(InventoryContainer.user_id == user_id)
    )
    if not all([profile, business, progression, inventory]):
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player state is incomplete.", status_code=500)

    room = await session.scalar(select(Room).where(Room.business_id == business.id))
    if room is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player room is missing.", status_code=500)

    slots = (
        await session.scalars(
            select(ProductionSlot)
            .where(ProductionSlot.room_id == room.id)
            .order_by(ProductionSlot.slot_index)
        )
    ).all()
    crops_by_slot = await get_active_crops_by_slot(session, [slot.id for slot in slots])
    state = await economy_state(session, user_id, now=now)
    premium_wallet = await session.scalar(select(PremiumWallet).where(PremiumWallet.user_id == user_id))
    active_entitlement_keys = list(
        (
            await session.scalars(
                select(PlayerEntitlement.entitlement_key)
                .where(
                    PlayerEntitlement.user_id == user_id,
                    PlayerEntitlement.status == "active",
                )
                .order_by(PlayerEntitlement.entitlement_key)
            )
        ).all()
    )
    meta = await meta_state(session, user_id, now=now, persist_bootstrap=True)
    skill_models = (
        await session.scalars(
            select(PlayerSkillBranch)
            .where(PlayerSkillBranch.user_id == user_id)
            .order_by(PlayerSkillBranch.branch)
        )
    ).all()

    return PlayerResponse(
        server_time=now,
        user_id=user.id,
        email=user.email,
        display_name=profile.display_name,
        business_id=business.id,
        business_name=business.name,
        room_id=room.id,
        room_slug=room.slug,
        room_level=room.level,
        slots=[slot_response(slot, crops_by_slot.get(slot.id), now) for slot in slots],
        level=progression.level,
        xp=progression.xp,
        next_level_xp=next_level_xp(progression.level),
        reputation=progression.reputation,
        skill_points_unspent=progression.skill_points_unspent,
        skill_branches=[
            SkillBranchResponse(
                branch=item.branch,
                label=skill_branch_label(item.branch),
                points=item.points,
                max_points=SKILL_MAX_POINTS,
                next_tier=skill_next_tier_label(item.branch, item.points),
            )
            for item in skill_models
        ],
        unlocked_keys=unlocked_keys(progression.level),
        tutorial_step=profile.tutorial_step,
        tutorial_completed=profile.tutorial_completed,
        inventory_container_id=inventory.id,
        inventory=await inventory_responses(session, inventory.id),
        inventory_lots=await inventory_lot_responses(session, inventory.id),
        starter_varieties=starter_variety_responses(progression.level),
        cash=state.cash,
        premium_credits=premium_wallet.credits if premium_wallet else 0,
        active_entitlement_keys=active_entitlement_keys,
        contract_offers=state.contract_offers,
        contract_refresh_at=state.contract_refresh_at,
        active_contract=state.active_contract,
        active_contracts=state.active_contracts,
        upgrade_offers=state.upgrade_offers,
        owned_upgrade_keys=state.owned_upgrade_keys,
        contacts=meta.contacts,
        missions=meta.missions,
        daily_mission_keys=meta.daily_mission_keys,
        weekly_mission_keys=meta.weekly_mission_keys,
        mastery=meta.mastery,
        unlocked_cosmetic_keys=meta.unlocked_cosmetic_keys,
    )


def decode_user_id(access_token: str) -> uuid.UUID:
    from app.security import decode_access_token

    try:
        return decode_access_token(access_token)
    except jwt.InvalidTokenError as exc:
        raise AppError("AUTH_ACCESS_INVALID", "Access token is invalid.", status_code=401) from exc
