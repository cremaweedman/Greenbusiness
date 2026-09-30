from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.economy_service import (
    accept_contract,
    accept_offer,
    complete_contract,
    purchase_upgrade,
)
from app.liveops_service import require_feature_enabled
from app.schemas import EconomyActionResponse, PlayerContractResponse

economy_router = APIRouter(prefix="/economy", tags=["economy"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
IdempotencyKey = Annotated[
    str,
    Header(alias="Idempotency-Key", min_length=1, max_length=128),
]


@economy_router.post("/offers/{offer_id}/accept", response_model=PlayerContractResponse)
async def accept_current_offer(
    offer_id: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> PlayerContractResponse:
    await require_feature_enabled(session, "contracts")
    return await accept_offer(
        session,
        user_id=user_id,
        offer_id=offer_id,
        request_id=getattr(request.state, "request_id", None),
    )


@economy_router.post("/contracts/{contract_key}/accept", response_model=PlayerContractResponse)
async def accept_legacy_contract(
    contract_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> PlayerContractResponse:
    await require_feature_enabled(session, "contracts")
    return await accept_contract(
        session,
        user_id=user_id,
        contract_key=contract_key,
        request_id=getattr(request.state, "request_id", None),
    )


@economy_router.post("/contracts/{contract_id}/complete", response_model=EconomyActionResponse)
async def complete(
    contract_id: uuid.UUID,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
    idempotency_key: IdempotencyKey,
) -> EconomyActionResponse:
    await require_feature_enabled(session, "contracts")
    return await complete_contract(
        session,
        user_id=user_id,
        contract_id=contract_id,
        idempotency_key=idempotency_key,
        request_id=getattr(request.state, "request_id", None),
    )


@economy_router.post("/upgrades/{upgrade_key}/purchase", response_model=EconomyActionResponse)
async def purchase(
    upgrade_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
    idempotency_key: IdempotencyKey,
) -> EconomyActionResponse:
    await require_feature_enabled(session, "upgrades")
    return await purchase_upgrade(
        session,
        user_id=user_id,
        upgrade_key=upgrade_key,
        idempotency_key=idempotency_key,
        request_id=getattr(request.state, "request_id", None),
    )
