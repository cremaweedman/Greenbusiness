from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.config import settings
from app.db.models import (
    AuthSession,
    Business,
    InventoryContainer,
    PlayerProfile,
    ProductionSlot,
    Progression,
    Room,
    User,
)
from app.errors import AppError
from app.schemas import PlayerResponse, ProductionSlotResponse
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

    user = User(email=normalized, password_hash=hash_password(password))
    session.add(user)
    await session.flush()

    profile = PlayerProfile(user_id=user.id, display_name=display_name.strip())
    business = Business(user_id=user.id, name=f"{display_name.strip()}'s GreenBusiness")
    progression = Progression(user_id=user.id, level=1, xp=0, reputation=0)
    inventory = InventoryContainer(user_id=user.id, kind="main")

    session.add_all([profile, business, progression, inventory])
    await session.flush()

    room = Room(business_id=business.id, slug="starter-growroom", level=1)
    session.add(room)
    await session.flush()

    session.add_all(
        [
            ProductionSlot(room_id=room.id, slot_index=0, status="available"),
            ProductionSlot(room_id=room.id, slot_index=1, status="available"),
        ]
    )

    refresh_token = new_refresh_token()
    auth_session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.refresh_ttl_seconds),
    )
    session.add(auth_session)

    await append_audit_event(
        session,
        event_type="auth.user_registered",
        actor_type="user",
        actor_id=str(user.id),
        target_type="user",
        target_id=str(user.id),
        request_id=request_id,
        payload={"email": normalized},
    )

    await session.commit()
    return user, create_access_token(user.id), refresh_token


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

    return PlayerResponse(
        user_id=user.id,
        email=user.email,
        display_name=profile.display_name,
        business_id=business.id,
        business_name=business.name,
        room_id=room.id,
        room_slug=room.slug,
        room_level=room.level,
        slots=[
            ProductionSlotResponse(id=slot.id, slot_index=slot.slot_index, status=slot.status)
            for slot in slots
        ],
        level=progression.level,
        xp=progression.xp,
        reputation=progression.reputation,
        inventory_container_id=inventory.id,
    )


def decode_user_id(access_token: str) -> uuid.UUID:
    from app.security import decode_access_token

    try:
        return decode_access_token(access_token)
    except jwt.InvalidTokenError as exc:
        raise AppError("AUTH_ACCESS_INVALID", "Access token is invalid.", status_code=401) from exc
