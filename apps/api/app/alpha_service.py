from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import AlphaFeedback, AnalyticsEvent, PlayerProfile, User
from app.errors import AppError
from app.liveops_service import record_analytics_event
from app.schemas import (
    AlphaFeedbackCreateRequest,
    AlphaFeedbackResponse,
    AlphaFeedbackTriageRequest,
    AlphaRetentionDashboardResponse,
)

PLAYER_ACTIVITY_PREFIXES = ("auth.", "production.", "economy.", "meta.", "social.", "clubs.", "store.")


def _response(row: AlphaFeedback) -> AlphaFeedbackResponse:
    return AlphaFeedbackResponse(
        id=row.id,
        user_id=row.user_id,
        kind=row.kind,
        severity=row.severity,
        category=row.category,
        message=row.message,
        build_sha=row.build_sha,
        liveops_version=row.liveops_version,
        status=row.status,
        triaged_by=row.triaged_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


async def submit_alpha_feedback(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    body: AlphaFeedbackCreateRequest,
    request_id: str | None,
) -> AlphaFeedbackResponse:
    row = AlphaFeedback(
        user_id=user_id,
        kind=body.kind,
        severity=body.severity,
        category=body.category.strip().lower(),
        message=body.message.strip(),
        build_sha=body.build_sha.strip() if body.build_sha else None,
        liveops_version=body.liveops_version,
    )
    session.add(row)
    await session.flush()
    await record_analytics_event(
        session,
        event_name="alpha.feedback_submitted",
        user_id=user_id,
        payload={
            "kind": row.kind,
            "severity": row.severity,
            "category": row.category,
            "build_sha": row.build_sha,
            "liveops_version": row.liveops_version,
        },
        request_id=request_id,
    )
    await session.commit()
    return _response(row)


async def list_alpha_feedback(
    session: AsyncSession,
    *,
    status: str | None,
    limit: int,
) -> list[AlphaFeedbackResponse]:
    query = select(AlphaFeedback).order_by(desc(AlphaFeedback.created_at))
    if status is not None:
        query = query.where(AlphaFeedback.status == status)
    rows = (await session.scalars(query.limit(max(1, min(limit, 200))))).all()
    return [_response(row) for row in rows]


async def triage_alpha_feedback(
    session: AsyncSession,
    *,
    feedback_id: uuid.UUID,
    body: AlphaFeedbackTriageRequest,
    admin_actor_id: str,
    request_id: str | None,
) -> AlphaFeedbackResponse:
    row = await session.scalar(
        select(AlphaFeedback).where(AlphaFeedback.id == feedback_id).with_for_update()
    )
    if row is None:
        raise AppError("ALPHA_FEEDBACK_NOT_FOUND", "Alpha feedback was not found.", status_code=404)
    before = {"status": row.status, "severity": row.severity}
    row.status = body.status
    if body.severity is not None:
        row.severity = body.severity
    row.triaged_by = admin_actor_id
    await append_audit_event(
        session,
        event_type="admin.alpha_feedback_triaged",
        actor_type="admin",
        actor_id=admin_actor_id,
        target_type="alpha_feedback",
        target_id=str(row.id),
        request_id=request_id,
        payload={
            "before": before,
            "after": {"status": row.status, "severity": row.severity},
        },
    )
    await session.commit()
    await session.refresh(row)
    return _response(row)


async def alpha_retention_dashboard(session: AsyncSession) -> AlphaRetentionDashboardResponse:
    now = datetime.now(UTC)
    users = (await session.execute(select(User.id, User.created_at))).all()
    profiles = dict(
        (await session.execute(select(PlayerProfile.user_id, PlayerProfile.tutorial_completed))).all()
    )
    events = (
        await session.execute(
            select(AnalyticsEvent.user_id, AnalyticsEvent.event_name, AnalyticsEvent.created_at)
            .where(AnalyticsEvent.user_id.is_not(None))
            .order_by(AnalyticsEvent.created_at)
        )
    ).all()
    by_user: dict[uuid.UUID, list[tuple[str, datetime]]] = defaultdict(list)
    for user_id, event_name, created_at in events:
        if user_id is not None and created_at is not None:
            by_user[user_id].append((event_name, created_at))

    cohort_size = len(users)
    tutorial_completed = sum(1 for user_id, _ in users if profiles.get(user_id, False))
    first_harvest_users = sum(
        1
        for user_id, _ in users
        if any(name == "production.crop_harvested" for name, _at in by_user.get(user_id, []))
    )

    d1_eligible = d1_returned = d7_eligible = d7_returned = 0
    for user_id, created_at in users:
        if created_at is None:
            continue
        activity = [
            at
            for name, at in by_user.get(user_id, [])
            if name.startswith(PLAYER_ACTIVITY_PREFIXES)
        ]
        if now >= created_at + timedelta(days=2):
            d1_eligible += 1
            if any(created_at + timedelta(days=1) <= at < created_at + timedelta(days=2) for at in activity):
                d1_returned += 1
        if now >= created_at + timedelta(days=8):
            d7_eligible += 1
            if any(created_at + timedelta(days=7) <= at < created_at + timedelta(days=8) for at in activity):
                d7_returned += 1

    open_blockers = int(
        await session.scalar(
            select(func.count()).select_from(AlphaFeedback).where(
                AlphaFeedback.severity == "blocker",
                AlphaFeedback.status.in_(("new", "triaged")),
            )
        ) or 0
    )
    open_major = int(
        await session.scalar(
            select(func.count()).select_from(AlphaFeedback).where(
                AlphaFeedback.severity == "major",
                AlphaFeedback.status.in_(("new", "triaged")),
            )
        ) or 0
    )
    feedback_new = int(
        await session.scalar(
            select(func.count()).select_from(AlphaFeedback).where(AlphaFeedback.status == "new")
        ) or 0
    )

    return AlphaRetentionDashboardResponse(
        cohort_size=cohort_size,
        tutorial_completed=tutorial_completed,
        first_harvest_users=first_harvest_users,
        d1_eligible=d1_eligible,
        d1_returned=d1_returned,
        d1_rate=round(d1_returned / d1_eligible, 4) if d1_eligible else 0.0,
        d7_eligible=d7_eligible,
        d7_returned=d7_returned,
        d7_rate=round(d7_returned / d7_eligible, 4) if d7_eligible else 0.0,
        open_blockers=open_blockers,
        open_major=open_major,
        feedback_new=feedback_new,
    )
