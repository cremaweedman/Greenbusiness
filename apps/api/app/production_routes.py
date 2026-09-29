from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.production_service import care_for_crop, harvest_crop, plant_crop
from app.schemas import HarvestResponse, PlantRequest, ProductionSlotResponse

production_router = APIRouter(prefix="/production", tags=["production"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@production_router.post("/slots/{slot_id}/plant", response_model=ProductionSlotResponse)
async def plant(
    slot_id: uuid.UUID,
    body: PlantRequest,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> ProductionSlotResponse:
    return await plant_crop(
        session,
        user_id=user_id,
        slot_id=slot_id,
        variety_key=body.variety_key,
        request_id=getattr(request.state, "request_id", None),
    )


@production_router.post("/slots/{slot_id}/care", response_model=ProductionSlotResponse)
async def care(
    slot_id: uuid.UUID,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> ProductionSlotResponse:
    return await care_for_crop(
        session,
        user_id=user_id,
        slot_id=slot_id,
        request_id=getattr(request.state, "request_id", None),
    )


@production_router.post("/slots/{slot_id}/harvest", response_model=HarvestResponse)
async def harvest(
    slot_id: uuid.UUID,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> HarvestResponse:
    return await harvest_crop(
        session,
        user_id=user_id,
        slot_id=slot_id,
        request_id=getattr(request.state, "request_id", None),
    )
