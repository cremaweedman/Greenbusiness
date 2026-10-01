from __future__ import annotations

import base64
import uuid
from hashlib import sha256

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import NotificationPreference, PushToken
from app.schemas import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
    NotificationStateResponse,
    PlatformReadinessResponse,
    PushTokenResponse,
)

SUPPORTED_PUSH_PLATFORMS = {"web", "android", "ios"}


def _valid_time(value: str) -> bool:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59


def _token_hash(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def _token_cipher() -> Fernet:
    key = settings.push_token_encryption_key.strip()
    if key:
        try:
            return Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise RuntimeError("PUSH_TOKEN_ENCRYPTION_KEY is not a valid Fernet key") from exc
    derived = base64.urlsafe_b64encode(sha256(settings.jwt_secret.encode("utf-8")).digest())
    return Fernet(derived)


def _encrypt_push_token(token: str) -> str:
    return _token_cipher().encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_push_token(model: PushToken) -> str | None:
    if not model.token_ciphertext:
        return None
    try:
        return _token_cipher().decrypt(model.token_ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None


def _token_label(token: str) -> str:
    return f"…{token[-6:]}"


async def ensure_notification_preferences(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> NotificationPreference:
    prefs = await session.scalar(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    if prefs is not None:
        return prefs
    prefs = NotificationPreference(user_id=user_id)
    session.add(prefs)
    await session.flush()
    return prefs


def _preference_response(prefs: NotificationPreference) -> NotificationPreferenceResponse:
    return NotificationPreferenceResponse(
        production_enabled=prefs.production_enabled,
        events_enabled=prefs.events_enabled,
        social_enabled=prefs.social_enabled,
        quiet_hours_enabled=prefs.quiet_hours_enabled,
        quiet_hours_start=prefs.quiet_hours_start,
        quiet_hours_end=prefs.quiet_hours_end,
        timezone=prefs.timezone,
        updated_at=prefs.updated_at,
    )


def _push_token_response(token: PushToken) -> PushTokenResponse:
    return PushTokenResponse(
        id=token.id,
        platform=token.platform,
        token_label=token.token_label,
        enabled=token.enabled,
        created_at=token.created_at,
        updated_at=token.updated_at,
    )


async def notification_state(session: AsyncSession, user_id: uuid.UUID) -> NotificationStateResponse:
    prefs = await ensure_notification_preferences(session, user_id)
    await session.flush()
    await session.refresh(prefs)
    tokens = (
        await session.scalars(
            select(PushToken)
            .where(PushToken.user_id == user_id)
            .order_by(PushToken.created_at, PushToken.id)
        )
    ).all()
    await session.commit()
    return NotificationStateResponse(
        preferences=_preference_response(prefs),
        push_tokens=[_push_token_response(token) for token in tokens],
        deep_links={
            "home": "greenbusiness://home",
            "production": "greenbusiness://production",
            "club": "greenbusiness://club",
            "store": "greenbusiness://store",
        },
        pwa={
            "installable": True,
            "offline_read_cache": True,
            "manifest_path": "/manifest.webmanifest",
        },
    )


async def update_notification_preferences(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    body: NotificationPreferenceUpdateRequest,
) -> NotificationPreferenceResponse:
    prefs = await ensure_notification_preferences(session, user_id)
    updates = body.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if value is None:
            continue
        if key in {"quiet_hours_start", "quiet_hours_end"} and not _valid_time(value):
            from app.errors import AppError

            raise AppError(
                "NOTIFICATION_TIME_INVALID",
                "Quiet hour values must be valid HH:MM times.",
                status_code=400,
            )
        setattr(prefs, key, value)
    await session.commit()
    await session.refresh(prefs)
    return _preference_response(prefs)


async def register_push_token(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    platform: str,
    token: str,
) -> PushTokenResponse:
    from app.errors import AppError

    platform_key = platform.lower().strip()
    if platform_key not in SUPPORTED_PUSH_PLATFORMS:
        raise AppError(
            "PUSH_PLATFORM_UNSUPPORTED",
            "Push platform is not supported.",
            status_code=400,
        )
    hashed = _token_hash(token)
    model = await session.scalar(
        select(PushToken).where(PushToken.user_id == user_id, PushToken.token_hash == hashed)
    )
    if model is None:
        model = PushToken(
            user_id=user_id,
            platform=platform_key,
            token_hash=hashed,
            token_ciphertext=_encrypt_push_token(token),
            token_label=_token_label(token),
            enabled=True,
        )
        session.add(model)
        await session.flush()
    else:
        model.platform = platform_key
        model.token_ciphertext = _encrypt_push_token(token)
        model.enabled = True
    await session.commit()
    await session.refresh(model)
    return _push_token_response(model)


async def disable_push_token(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    token_id: uuid.UUID,
) -> PushTokenResponse:
    from app.errors import AppError

    token = await session.scalar(
        select(PushToken).where(PushToken.id == token_id, PushToken.user_id == user_id)
    )
    if token is None:
        raise AppError("PUSH_TOKEN_NOT_FOUND", "Push token was not found.", status_code=404)
    token.enabled = False
    await session.commit()
    await session.refresh(token)
    return _push_token_response(token)


def platform_readiness() -> PlatformReadinessResponse:
    return PlatformReadinessResponse(
        pwa_installable=True,
        android_packaging_path="Capacitor or Trusted Web Activity from the PWA shell",
        ios_packaging_path="Capacitor iOS adapter prepared; release requires cannabis-policy review",
        ios_release_requires_policy_review=True,
    )
