from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.alpha_service import (
    alpha_retention_dashboard,
    enroll_alpha_member,
    list_alpha_feedback,
    list_alpha_members,
    submit_alpha_feedback,
    triage_alpha_feedback,
)
from app.dependencies import (
    get_admin_actor_id,
    get_admin_operator_id,
    get_current_user_id,
    get_db,
)
from app.schemas import (
    AlphaCohortEnrollRequest,
    AlphaCohortMemberResponse,
    AlphaFeedbackCreateRequest,
    AlphaFeedbackResponse,
    AlphaFeedbackTriageRequest,
    AlphaRetentionDashboardResponse,
)

alpha_router = APIRouter(prefix="/alpha", tags=["alpha"])
admin_alpha_router = APIRouter(prefix="/admin/alpha", tags=["admin-alpha"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
AdminActor = Annotated[str, Depends(get_admin_actor_id)]
AdminOperator = Annotated[str, Depends(get_admin_operator_id)]


@alpha_router.post("/feedback", response_model=AlphaFeedbackResponse, status_code=201)
async def create_alpha_feedback(
    body: AlphaFeedbackCreateRequest,
    request: Request,
    user_id: CurrentUserId,
    session: DbSession,
) -> AlphaFeedbackResponse:
    return await submit_alpha_feedback(
        session,
        user_id=user_id,
        body=body,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_alpha_router.get("/feedback", response_model=list[AlphaFeedbackResponse])
async def read_alpha_feedback(
    session: DbSession,
    _admin_actor: AdminActor,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[AlphaFeedbackResponse]:
    return await list_alpha_feedback(session, status=status, limit=limit)


@admin_alpha_router.patch("/feedback/{feedback_id}", response_model=AlphaFeedbackResponse)
async def update_alpha_feedback(
    feedback_id: uuid.UUID,
    body: AlphaFeedbackTriageRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminOperator,
) -> AlphaFeedbackResponse:
    return await triage_alpha_feedback(
        session,
        feedback_id=feedback_id,
        body=body,
        admin_actor_id=admin_actor,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_alpha_router.get("/dashboard", response_model=AlphaRetentionDashboardResponse)
async def read_alpha_dashboard(
    session: DbSession,
    _admin_actor: AdminActor,
) -> AlphaRetentionDashboardResponse:
    return await alpha_retention_dashboard(session)


@admin_alpha_router.post(
    "/cohort/{user_id}",
    response_model=AlphaCohortMemberResponse,
    status_code=201,
)
async def enroll_alpha_cohort_member(
    user_id: uuid.UUID,
    body: AlphaCohortEnrollRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminOperator,
) -> AlphaCohortMemberResponse:
    return await enroll_alpha_member(
        session,
        user_id=user_id,
        body=body,
        admin_actor_id=admin_actor,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_alpha_router.get("/cohort", response_model=list[AlphaCohortMemberResponse])
async def read_alpha_cohort(
    session: DbSession,
    _admin_actor: AdminActor,
    limit: int = Query(default=100, ge=1, le=200),
) -> list[AlphaCohortMemberResponse]:
    return await list_alpha_members(session, limit=limit)
