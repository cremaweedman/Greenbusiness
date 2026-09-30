from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts_service import (
    complete_contract,
    get_contract_board,
    list_contracts,
    reroll_contract_board,
)
from app.dependencies import get_current_user_id, get_db
from app.schemas import (
    ContractBoardResponse,
    ContractCompletionResponse,
    ContractRerollResponse,
    ContractResponse,
)

contracts_router = APIRouter(prefix="/contracts", tags=["contracts"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@contracts_router.get("", response_model=list[ContractResponse])
async def list_available_contracts(
    user_id: CurrentUserId,
    session: DbSession,
) -> list[ContractResponse]:
    return await list_contracts(session, user_id=user_id)


@contracts_router.get("/board", response_model=ContractBoardResponse)
async def get_board(
    user_id: CurrentUserId,
    session: DbSession,
) -> ContractBoardResponse:
    return await get_contract_board(session, user_id=user_id)


@contracts_router.post("/reroll", response_model=ContractRerollResponse)
async def reroll(
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> ContractRerollResponse:
    return await reroll_contract_board(
        session,
        user_id=user_id,
        request_id=getattr(request.state, "request_id", None),
    )


@contracts_router.post("/{contract_key}/complete", response_model=ContractCompletionResponse)
async def complete(
    contract_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> ContractCompletionResponse:
    return await complete_contract(
        session,
        user_id=user_id,
        contract_key=contract_key,
        request_id=getattr(request.state, "request_id", None),
    )
