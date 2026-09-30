from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts_service import complete_contract
from app.dependencies import get_current_user_id, get_db
from app.schemas import ContractCompletionResponse

contracts_router = APIRouter(prefix="/contracts", tags=["contracts"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


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
