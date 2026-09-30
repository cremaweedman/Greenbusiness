from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.schemas import UpgradePurchaseResponse, UpgradeResponse
from app.upgrades_service import purchase_upgrade, upgrade_responses

upgrades_router = APIRouter(prefix="/upgrades", tags=["upgrades"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@upgrades_router.get("", response_model=list[UpgradeResponse])
async def list_upgrades(
    user_id: CurrentUserId,
    session: DbSession,
) -> list[UpgradeResponse]:
    return await upgrade_responses(session, user_id=user_id)


@upgrades_router.post("/{upgrade_key}/purchase", response_model=UpgradePurchaseResponse)
async def purchase(
    upgrade_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> UpgradePurchaseResponse:
    return await purchase_upgrade(
        session,
        user_id=user_id,
        upgrade_key=upgrade_key,
        request_id=getattr(request.state, "request_id", None),
    )
