from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts_service import cash_ledger_entries, cash_summary
from app.dependencies import get_current_user_id, get_db
from app.schemas import CurrencyLedgerEntryResponse, EconomySummaryResponse

economy_router = APIRouter(prefix="/economy", tags=["economy"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@economy_router.get("/cash-ledger", response_model=list[CurrencyLedgerEntryResponse])
async def list_cash_ledger(
    user_id: CurrentUserId,
    session: DbSession,
) -> list[CurrencyLedgerEntryResponse]:
    return await cash_ledger_entries(session, user_id=user_id)


@economy_router.get("/summary", response_model=EconomySummaryResponse)
async def get_economy_summary(
    user_id: CurrentUserId,
    session: DbSession,
) -> EconomySummaryResponse:
    return await cash_summary(session, user_id=user_id)
