from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_admin_actor_id, get_current_user_id, get_db
from app.liveops_service import (
    active_config,
    admin_cash_mutation,
    admin_player_lookup,
    core_funnel,
    core_loop_dashboard,
    economy_dashboard,
    experiment_assignments,
    ledger_entries,
    list_config_versions,
    publish_config,
    recent_analytics_events,
    rollback_config,
)
from app.schemas import (
    AdminCashMutationRequest,
    AdminCashMutationResponse,
    AdminLedgerEntryResponse,
    AdminPlayerLookupResponse,
    AnalyticsEventResponse,
    CoreFunnelResponse,
    CoreLoopDashboardResponse,
    EconomyDashboardResponse,
    ExperimentAssignmentResponse,
    LiveOpsConfigPublishRequest,
    LiveOpsConfigResponse,
    LiveOpsConfigRollbackRequest,
)

admin_router = APIRouter(prefix="/admin", tags=["admin"])
liveops_router = APIRouter(prefix="/liveops", tags=["liveops"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
AdminActor = Annotated[str, Depends(get_admin_actor_id)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


@liveops_router.get("/config", response_model=LiveOpsConfigResponse)
async def get_active_public_config(session: DbSession) -> LiveOpsConfigResponse:
    return await active_config(session)


@liveops_router.get("/experiments", response_model=ExperimentAssignmentResponse)
async def get_experiment_assignments(
    request: Request,
    session: DbSession,
    user_id: CurrentUserId,
) -> ExperimentAssignmentResponse:
    return await experiment_assignments(
        session,
        user_id=user_id,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_router.get("/config/active", response_model=LiveOpsConfigResponse)
async def get_active_admin_config(
    session: DbSession,
    _admin_actor: AdminActor,
) -> LiveOpsConfigResponse:
    return await active_config(session)


@admin_router.get("/config/versions", response_model=list[LiveOpsConfigResponse])
async def list_admin_config_versions(
    session: DbSession,
    _admin_actor: AdminActor,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[LiveOpsConfigResponse]:
    return await list_config_versions(session, limit=limit)


@admin_router.post("/config/publish", response_model=LiveOpsConfigResponse)
async def publish_admin_config(
    body: LiveOpsConfigPublishRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminActor,
) -> LiveOpsConfigResponse:
    return await publish_config(
        session,
        config=body.config,
        admin_actor_id=admin_actor,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_router.post("/config/rollback", response_model=LiveOpsConfigResponse)
async def rollback_admin_config(
    body: LiveOpsConfigRollbackRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminActor,
) -> LiveOpsConfigResponse:
    return await rollback_config(
        session,
        source_version=body.source_version,
        admin_actor_id=admin_actor,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_router.get("/players/{user_id}", response_model=AdminPlayerLookupResponse)
async def lookup_player(
    user_id: uuid.UUID,
    session: DbSession,
    _admin_actor: AdminActor,
) -> AdminPlayerLookupResponse:
    return await admin_player_lookup(session, user_id=user_id)


@admin_router.get("/ledger", response_model=list[AdminLedgerEntryResponse])
async def inspect_ledger(
    session: DbSession,
    _admin_actor: AdminActor,
    user_id: uuid.UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AdminLedgerEntryResponse]:
    return await ledger_entries(session, user_id=user_id, limit=limit)


@admin_router.post("/cash/grant", response_model=AdminCashMutationResponse)
async def grant_cash(
    body: AdminCashMutationRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminActor,
) -> AdminCashMutationResponse:
    return await admin_cash_mutation(
        session,
        user_id=body.user_id,
        amount=body.amount,
        source_or_sink="admin_grant",
        admin_actor_id=admin_actor,
        reason=body.reason,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_router.post("/cash/revoke", response_model=AdminCashMutationResponse)
async def revoke_cash(
    body: AdminCashMutationRequest,
    request: Request,
    session: DbSession,
    admin_actor: AdminActor,
) -> AdminCashMutationResponse:
    return await admin_cash_mutation(
        session,
        user_id=body.user_id,
        amount=body.amount,
        source_or_sink="admin_revoke",
        admin_actor_id=admin_actor,
        reason=body.reason,
        request_id=getattr(request.state, "request_id", None),
    )


@admin_router.get("/dashboards/economy", response_model=EconomyDashboardResponse)
async def read_economy_dashboard(
    session: DbSession,
    _admin_actor: AdminActor,
) -> EconomyDashboardResponse:
    return await economy_dashboard(session)


@admin_router.get("/dashboards/core-funnel", response_model=CoreFunnelResponse)
async def read_core_funnel(
    session: DbSession,
    _admin_actor: AdminActor,
) -> CoreFunnelResponse:
    return await core_funnel(session)


@admin_router.get("/dashboards/core-loop", response_model=CoreLoopDashboardResponse)
async def read_core_loop_dashboard(
    session: DbSession,
    _admin_actor: AdminActor,
) -> CoreLoopDashboardResponse:
    return await core_loop_dashboard(session)


@admin_router.get("/analytics/events", response_model=list[AnalyticsEventResponse])
async def read_recent_analytics_events(
    session: DbSession,
    _admin_actor: AdminActor,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AnalyticsEventResponse]:
    return await recent_analytics_events(session, limit=limit)
