from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.schemas import SkillAllocationResponse, SkillNodeResponse
from app.skills_service import allocate_skill, respec_skills, skill_responses

skills_router = APIRouter(prefix="/skills", tags=["skills"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@skills_router.get("", response_model=list[SkillNodeResponse])
async def list_skills(
    user_id: CurrentUserId,
    session: DbSession,
) -> list[SkillNodeResponse]:
    return await skill_responses(session, user_id=user_id)


@skills_router.post("/{skill_key}/allocate", response_model=SkillAllocationResponse)
async def allocate(
    skill_key: str,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> SkillAllocationResponse:
    return await allocate_skill(
        session,
        user_id=user_id,
        skill_key=skill_key,
        request_id=getattr(request.state, "request_id", None),
    )


@skills_router.post("/respec", response_model=SkillAllocationResponse)
async def respec(
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> SkillAllocationResponse:
    return await respec_skills(
        session,
        user_id=user_id,
        request_id=getattr(request.state, "request_id", None),
    )
