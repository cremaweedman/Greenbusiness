from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.notification_service import (
    disable_push_token,
    notification_state,
    platform_readiness,
    register_push_token,
    update_notification_preferences,
)
from app.schemas import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
    NotificationStateResponse,
    PlatformReadinessResponse,
    PushTokenRegisterRequest,
    PushTokenResponse,
)

notification_router = APIRouter(prefix="/notifications", tags=["notifications"])
platform_router = APIRouter(prefix="/platform", tags=["platform"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@notification_router.get("/me", response_model=NotificationStateResponse)
async def get_notifications(
    user_id: CurrentUserId,
    session: DbSession,
) -> NotificationStateResponse:
    return await notification_state(session, user_id)


@notification_router.patch("/preferences", response_model=NotificationPreferenceResponse)
async def update_preferences(
    body: NotificationPreferenceUpdateRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> NotificationPreferenceResponse:
    return await update_notification_preferences(session, user_id=user_id, body=body)


@notification_router.post("/push-tokens", response_model=PushTokenResponse, status_code=201)
async def add_push_token(
    body: PushTokenRegisterRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> PushTokenResponse:
    return await register_push_token(
        session,
        user_id=user_id,
        platform=body.platform,
        token=body.token,
    )


@notification_router.post("/push-tokens/{token_id}/disable", response_model=PushTokenResponse)
async def disable_token(
    token_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> PushTokenResponse:
    return await disable_push_token(session, user_id=user_id, token_id=token_id)


@platform_router.get("/readiness", response_model=PlatformReadinessResponse)
async def readiness() -> PlatformReadinessResponse:
    return platform_readiness()
