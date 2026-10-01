from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.decoration_service import decoration_state, equip_decoration, purchase_decoration
from app.dependencies import get_current_user_id, get_db
from app.schemas import (
    DecorationEquipRequest,
    DecorationEquipResponse,
    DecorationPurchaseResponse,
    DecorationStateResponse,
)

decoration_router = APIRouter(prefix="/decorations", tags=["decorations"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=128)]


@decoration_router.get("/me", response_model=DecorationStateResponse)
async def get_decorations(
    user_id: CurrentUserId,
    session: DbSession,
) -> DecorationStateResponse:
    return await decoration_state(session, user_id)


@decoration_router.post("/{decoration_key}/purchase", response_model=DecorationPurchaseResponse)
async def purchase(
    decoration_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
    idempotency_key: IdempotencyKey,
) -> DecorationPurchaseResponse:
    return await purchase_decoration(
        session,
        user_id=user_id,
        decoration_key=decoration_key,
        idempotency_key=idempotency_key,
        request_id=getattr(request.state, "request_id", None),
    )


@decoration_router.put("/{decoration_key}/equip", response_model=DecorationEquipResponse)
async def equip(
    decoration_key: str,
    body: DecorationEquipRequest,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> DecorationEquipResponse:
    return await equip_decoration(
        session,
        user_id=user_id,
        decoration_key=decoration_key,
        slot_index=body.slot_index,
        request_id=getattr(request.state, "request_id", None),
    )
