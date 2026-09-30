from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import PlayerSkillAllocation, Progression
from app.errors import AppError
from app.game_data.skills_catalog import SKILL_BY_KEY, SKILLS, SkillNode
from app.progression_service import progression_response
from app.schemas import SkillAllocationResponse, SkillEffectsResponse, SkillNodeResponse


@dataclass(frozen=True)
class PlayerSkillEffects:
    care_yield_bonus: int = 0
    contract_cash_bonus: int = 0
    grow_seconds_reduction: int = 0


async def _allocation_ranks(session: AsyncSession, user_id: uuid.UUID) -> dict[str, int]:
    allocations = (
        await session.scalars(
            select(PlayerSkillAllocation).where(PlayerSkillAllocation.user_id == user_id)
        )
    ).all()
    return {allocation.skill_key: allocation.rank for allocation in allocations}


def _skill_response(
    skill: SkillNode,
    *,
    rank: int,
    available_points: int,
) -> SkillNodeResponse:
    return SkillNodeResponse(
        key=skill.key,
        branch=skill.branch,
        name=skill.name,
        description=skill.description,
        rank=rank,
        max_rank=skill.max_rank,
        cost_per_rank=skill.cost_per_rank,
        can_allocate=rank < skill.max_rank and available_points >= skill.cost_per_rank,
        effects=SkillEffectsResponse(
            care_yield_bonus=skill.effects.care_yield_bonus,
            contract_cash_bonus=skill.effects.contract_cash_bonus,
            grow_seconds_reduction=skill.effects.grow_seconds_reduction,
        ),
    )


async def skill_responses(session: AsyncSession, *, user_id: uuid.UUID) -> list[SkillNodeResponse]:
    progression = await session.scalar(select(Progression).where(Progression.user_id == user_id))
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)
    ranks = await _allocation_ranks(session, user_id)
    return [
        _skill_response(skill, rank=ranks.get(skill.key, 0), available_points=progression.skill_points)
        for skill in SKILLS
    ]


async def player_skill_effects(session: AsyncSession, *, user_id: uuid.UUID) -> PlayerSkillEffects:
    ranks = await _allocation_ranks(session, user_id)
    return PlayerSkillEffects(
        care_yield_bonus=sum(
            skill.effects.care_yield_bonus * ranks.get(skill.key, 0)
            for skill in SKILLS
        ),
        contract_cash_bonus=sum(
            skill.effects.contract_cash_bonus * ranks.get(skill.key, 0)
            for skill in SKILLS
        ),
        grow_seconds_reduction=sum(
            skill.effects.grow_seconds_reduction * ranks.get(skill.key, 0)
            for skill in SKILLS
        ),
    )


async def allocate_skill(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    skill_key: str,
    request_id: str | None,
) -> SkillAllocationResponse:
    skill = SKILL_BY_KEY.get(skill_key)
    if skill is None:
        raise AppError("SKILL_NOT_FOUND", "Skill is not available.", status_code=404)

    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)
    if progression.skill_points < skill.cost_per_rank:
        raise AppError("SKILL_POINTS_INSUFFICIENT", "Not enough skill points.", status_code=409)

    allocation = await session.scalar(
        select(PlayerSkillAllocation)
        .where(PlayerSkillAllocation.user_id == user_id)
        .where(PlayerSkillAllocation.skill_key == skill.key)
        .with_for_update()
    )
    if allocation is not None and allocation.rank >= skill.max_rank:
        raise AppError("SKILL_MAX_RANK", "Skill is already at max rank.", status_code=409)

    now = datetime.now(UTC)
    if allocation is None:
        allocation = PlayerSkillAllocation(
            user_id=user_id,
            skill_key=skill.key,
            rank=1,
            allocated_at=now,
        )
        session.add(allocation)
    else:
        allocation.rank += 1
        allocation.allocated_at = now
    progression.skill_points -= skill.cost_per_rank
    await append_audit_event(
        session,
        event_type="skills.skill_allocated",
        actor_type="user",
        actor_id=str(user_id),
        target_type="skill",
        target_id=skill.key,
        request_id=request_id,
        payload={"rank": allocation.rank, "remaining_skill_points": progression.skill_points},
    )
    await session.commit()

    skills = await skill_responses(session, user_id=user_id)
    return SkillAllocationResponse(
        skill=next(item for item in skills if item.key == skill.key),
        progression=progression_response(progression),
        skills=skills,
    )


async def respec_skills(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    request_id: str | None,
) -> SkillAllocationResponse:
    progression = await session.scalar(
        select(Progression).where(Progression.user_id == user_id).with_for_update()
    )
    if progression is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player progression is missing.", status_code=500)

    ranks = await _allocation_ranks(session, user_id)
    refunded = sum(
        SKILL_BY_KEY[skill_key].cost_per_rank * rank
        for skill_key, rank in ranks.items()
        if skill_key in SKILL_BY_KEY
    )
    await session.execute(delete(PlayerSkillAllocation).where(PlayerSkillAllocation.user_id == user_id))
    progression.skill_points += refunded
    await append_audit_event(
        session,
        event_type="skills.skills_respecced",
        actor_type="user",
        actor_id=str(user_id),
        request_id=request_id,
        payload={"refunded_skill_points": refunded, "skill_points": progression.skill_points},
    )
    await session.commit()

    skills = await skill_responses(session, user_id=user_id)
    return SkillAllocationResponse(
        skill=skills[0],
        progression=progression_response(progression),
        skills=skills,
    )
