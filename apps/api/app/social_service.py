from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from secrets import token_hex

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import append_audit_event
from app.db.models import (
    Club,
    ClubAssist,
    ClubContribution,
    ClubInvite,
    ClubMembership,
    ClubObjective,
    ClubReaction,
    ClubRewardClaim,
    EconomyLedger,
    Friendship,
    PlayerProfile,
    SocialProfile,
    Wallet,
)
from app.errors import AppError
from app.liveops_service import record_analytics_event
from app.schemas import (
    ClubAssistResponse,
    ClubContributionResponse,
    ClubInviteResponse,
    ClubMemberResponse,
    ClubObjectiveResponse,
    ClubReactionResponse,
    ClubResponse,
    ClubRewardClaimResponse,
    FriendResponse,
    SocialProfileResponse,
    SocialStateResponse,
)

CLUB_CONFIG_VERSION = "clubs_v1"
CLUB_MAX_MEMBERS = 30
WEEKLY_ASSIST_LIMIT = 5
CLUB_OBJECTIVE_TARGET = 10
CLUB_OBJECTIVE_REWARD_CASH = 75
ALLOWED_REACTIONS = {"cheer", "thanks", "sprout", "fire", "boost"}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "club"


def _week_key(now: datetime | None = None) -> str:
    year, week, _weekday = (now or datetime.now(UTC)).isocalendar()
    return f"{year}-W{week:02d}"


def _friend_code() -> str:
    return f"GB{token_hex(3).upper()}"


def _invite_code() -> str:
    return f"CL{token_hex(3).upper()}"


async def ensure_social_profile(session: AsyncSession, user_id: uuid.UUID) -> SocialProfile:
    profile = await session.scalar(select(SocialProfile).where(SocialProfile.user_id == user_id))
    if profile is not None:
        return profile

    for _attempt in range(8):
        try:
            async with session.begin_nested():
                profile = SocialProfile(user_id=user_id, friend_code=_friend_code())
                session.add(profile)
                await session.flush()
            return profile
        except IntegrityError:
            continue
    raise AppError("SOCIAL_CODE_FAILED", "Could not allocate a friend code.", status_code=500)


async def _profile_by_friend_code(session: AsyncSession, friend_code: str) -> SocialProfile:
    profile = await session.scalar(
        select(SocialProfile).where(SocialProfile.friend_code == friend_code.upper())
    )
    if profile is None:
        raise AppError("FRIEND_CODE_NOT_FOUND", "Friend code was not found.", status_code=404)
    return profile


async def _membership(session: AsyncSession, user_id: uuid.UUID) -> ClubMembership | None:
    return await session.scalar(select(ClubMembership).where(ClubMembership.user_id == user_id))


async def _require_membership(
    session: AsyncSession,
    *,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
) -> ClubMembership:
    membership = await session.scalar(
        select(ClubMembership).where(
            ClubMembership.club_id == club_id,
            ClubMembership.user_id == user_id,
        )
    )
    if membership is None:
        raise AppError("CLUB_MEMBERSHIP_REQUIRED", "You are not a member of this club.", status_code=403)
    return membership


async def _club_member_count(session: AsyncSession, club_id: uuid.UUID) -> int:
    return int(
        await session.scalar(
            select(func.count()).select_from(ClubMembership).where(ClubMembership.club_id == club_id)
        )
        or 0
    )


async def _weekly_objective(session: AsyncSession, club_id: uuid.UUID) -> ClubObjective:
    period_key = _week_key()
    objective = await session.scalar(
        select(ClubObjective)
        .where(ClubObjective.club_id == club_id, ClubObjective.period_key == period_key)
        .with_for_update()
    )
    if objective is not None:
        return objective

    objective = ClubObjective(
        club_id=club_id,
        period_key=period_key,
        objective_key="weekly_collective_assists",
        target_amount=CLUB_OBJECTIVE_TARGET,
        progress_amount=0,
        reward_cash=CLUB_OBJECTIVE_REWARD_CASH,
        status="active",
    )
    session.add(objective)
    await session.flush()
    return objective


def _objective_response(objective: ClubObjective | None) -> ClubObjectiveResponse | None:
    if objective is None:
        return None
    return ClubObjectiveResponse(
        id=objective.id,
        period_key=objective.period_key,
        objective_key=objective.objective_key,
        target_amount=objective.target_amount,
        progress_amount=objective.progress_amount,
        reward_cash=objective.reward_cash,
        status=objective.status,
        completed_at=objective.completed_at,
    )


async def _club_response(
    session: AsyncSession,
    club: Club,
    *,
    user_id: uuid.UUID | None = None,
) -> ClubResponse:
    objective = await _weekly_objective(session, club.id)
    rows = (
        await session.execute(
            select(ClubMembership, PlayerProfile)
            .join(PlayerProfile, PlayerProfile.user_id == ClubMembership.user_id)
            .where(ClubMembership.club_id == club.id)
            .order_by(ClubMembership.joined_at)
        )
    ).all()
    members = [
        ClubMemberResponse(
            user_id=membership.user_id,
            display_name=profile.display_name,
            role=membership.role,
            joined_at=membership.joined_at,
        )
        for membership, profile in rows
    ]
    user_role = next((item.role for item, _profile in rows if item.user_id == user_id), None)
    return ClubResponse(
        id=club.id,
        name=club.name,
        slug=club.slug,
        invite_code=club.invite_code,
        max_members=club.max_members,
        member_count=len(members),
        user_role=user_role,
        objective=_objective_response(objective),
        members=members,
    )


async def social_profile_response(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> SocialProfileResponse:
    profile = await ensure_social_profile(session, user_id)
    return SocialProfileResponse(
        user_id=user_id,
        friend_code=profile.friend_code,
        deep_link=f"greenbusiness://friend/{profile.friend_code}",
    )


async def list_friends(session: AsyncSession, user_id: uuid.UUID) -> list[FriendResponse]:
    rows = (
        await session.execute(
            select(Friendship, PlayerProfile, SocialProfile)
            .join(
                PlayerProfile,
                or_(
                    and_(
                        Friendship.requester_id == user_id,
                        PlayerProfile.user_id == Friendship.addressee_id,
                    ),
                    and_(
                        Friendship.addressee_id == user_id,
                        PlayerProfile.user_id == Friendship.requester_id,
                    ),
                ),
            )
            .join(SocialProfile, SocialProfile.user_id == PlayerProfile.user_id)
            .where(
                Friendship.status == "accepted",
                or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
            )
            .order_by(Friendship.created_at)
        )
    ).all()
    return [
        FriendResponse(
            user_id=profile.user_id,
            display_name=profile.display_name,
            friend_code=social.friend_code,
            since=friendship.created_at,
        )
        for friendship, profile, social in rows
    ]


async def redeem_friend_code(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    friend_code: str,
) -> FriendResponse:
    await ensure_social_profile(session, user_id)
    target = await _profile_by_friend_code(session, friend_code)
    if target.user_id == user_id:
        raise AppError("FRIEND_SELF", "You cannot add yourself as a friend.", status_code=409)

    first, second = sorted([user_id, target.user_id], key=str)
    friendship = await session.scalar(
        select(Friendship).where(
            Friendship.requester_id == first,
            Friendship.addressee_id == second,
        )
    )
    if friendship is None:
        friendship = Friendship(requester_id=first, addressee_id=second, status="accepted")
        session.add(friendship)
        await session.flush()
        await record_analytics_event(
            session,
            event_name="social.friend_added",
            user_id=user_id,
            payload={"friend_user_id": str(target.user_id)},
        )

    target_profile = await session.scalar(
        select(PlayerProfile).where(PlayerProfile.user_id == target.user_id)
    )
    if target_profile is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Friend profile is missing.", status_code=500)
    return FriendResponse(
        user_id=target.user_id,
        display_name=target_profile.display_name,
        friend_code=target.friend_code,
        since=friendship.created_at,
    )


async def _pending_invites(session: AsyncSession, user_id: uuid.UUID) -> list[ClubInviteResponse]:
    rows = (
        await session.execute(
            select(ClubInvite, Club)
            .join(Club, Club.id == ClubInvite.club_id)
            .where(ClubInvite.invitee_user_id == user_id, ClubInvite.status == "pending")
            .order_by(ClubInvite.created_at)
        )
    ).all()
    return [
        ClubInviteResponse(
            id=invite.id,
            club_id=club.id,
            club_name=club.name,
            inviter_user_id=invite.inviter_user_id,
            invitee_user_id=invite.invitee_user_id,
            status=invite.status,
            created_at=invite.created_at,
            responded_at=invite.responded_at,
        )
        for invite, club in rows
    ]


async def social_state(session: AsyncSession, user_id: uuid.UUID) -> SocialStateResponse:
    membership = await _membership(session, user_id)
    club_response = None
    if membership is not None:
        club = await session.get(Club, membership.club_id)
        if club is not None:
            club_response = await _club_response(session, club, user_id=user_id)
    return SocialStateResponse(
        profile=await social_profile_response(session, user_id),
        friends=await list_friends(session, user_id),
        club=club_response,
        pending_invites=await _pending_invites(session, user_id),
    )


async def create_club(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    name: str,
) -> ClubResponse:
    if await _membership(session, user_id) is not None:
        raise AppError("CLUB_ALREADY_JOINED", "You already belong to a club.", status_code=409)

    base_slug = _slugify(name)
    for attempt in range(8):
        suffix = token_hex(2) if attempt else token_hex(1)
        slug = f"{base_slug}-{suffix}"
        club = Club(
            owner_user_id=user_id,
            name=name,
            slug=slug,
            invite_code=_invite_code(),
            max_members=CLUB_MAX_MEMBERS,
            status="active",
        )
        session.add(club)
        try:
            await session.flush()
            break
        except IntegrityError:
            await session.rollback()
    else:
        raise AppError("CLUB_CREATE_FAILED", "Could not create club.", status_code=500)

    session.add(ClubMembership(club_id=club.id, user_id=user_id, role="owner"))
    await _weekly_objective(session, club.id)
    await append_audit_event(
        session,
        event_type="club.created",
        actor_type="player",
        actor_id=str(user_id),
        target_type="club",
        target_id=str(club.id),
        payload={"name": name},
    )
    await record_analytics_event(
        session,
        event_name="social.club_created",
        user_id=user_id,
        payload={"club_id": str(club.id)},
    )
    await session.commit()
    return await _club_response(session, club, user_id=user_id)


async def join_club_by_invite_code(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    invite_code: str,
) -> ClubResponse:
    if await _membership(session, user_id) is not None:
        raise AppError("CLUB_ALREADY_JOINED", "You already belong to a club.", status_code=409)
    club = await session.scalar(select(Club).where(Club.invite_code == invite_code.upper()))
    if club is None or club.status != "active":
        raise AppError("CLUB_INVITE_CODE_NOT_FOUND", "Club invite code was not found.", status_code=404)
    if await _club_member_count(session, club.id) >= club.max_members:
        raise AppError("CLUB_FULL", "This club is full.", status_code=409)
    session.add(ClubMembership(club_id=club.id, user_id=user_id, role="member"))
    await record_analytics_event(
        session,
        event_name="social.club_joined",
        user_id=user_id,
        payload={"club_id": str(club.id), "method": "invite_code"},
    )
    await session.commit()
    return await _club_response(session, club, user_id=user_id)


async def create_club_invite(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
    friend_code: str,
) -> ClubInviteResponse:
    await _require_membership(session, club_id=club_id, user_id=user_id)
    target = await _profile_by_friend_code(session, friend_code)
    if target.user_id == user_id:
        raise AppError("CLUB_INVITE_SELF", "You cannot invite yourself.", status_code=409)
    if await _membership(session, target.user_id) is not None:
        raise AppError("CLUB_INVITEE_ALREADY_JOINED", "Invitee already belongs to a club.", status_code=409)

    invite = await session.scalar(
        select(ClubInvite).where(
            ClubInvite.club_id == club_id,
            ClubInvite.invitee_user_id == target.user_id,
        )
    )
    if invite is None:
        invite = ClubInvite(
            club_id=club_id,
            inviter_user_id=user_id,
            invitee_user_id=target.user_id,
            status="pending",
        )
        session.add(invite)
        await session.flush()
    elif invite.status != "pending":
        invite.status = "pending"
        invite.inviter_user_id = user_id
        invite.responded_at = None

    club = await session.get(Club, club_id)
    if club is None:
        raise AppError("CLUB_NOT_FOUND", "Club not found.", status_code=404)
    await session.commit()
    return ClubInviteResponse(
        id=invite.id,
        club_id=club.id,
        club_name=club.name,
        inviter_user_id=invite.inviter_user_id,
        invitee_user_id=invite.invitee_user_id,
        status=invite.status,
        created_at=invite.created_at,
        responded_at=invite.responded_at,
    )


async def accept_club_invite(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    invite_id: uuid.UUID,
) -> ClubResponse:
    if await _membership(session, user_id) is not None:
        raise AppError("CLUB_ALREADY_JOINED", "You already belong to a club.", status_code=409)
    invite = await session.get(ClubInvite, invite_id)
    if invite is None or invite.invitee_user_id != user_id:
        raise AppError("CLUB_INVITE_NOT_FOUND", "Club invite was not found.", status_code=404)
    if invite.status != "pending":
        raise AppError("CLUB_INVITE_NOT_PENDING", "Club invite is not pending.", status_code=409)
    club = await session.get(Club, invite.club_id)
    if club is None or club.status != "active":
        raise AppError("CLUB_NOT_FOUND", "Club not found.", status_code=404)
    if await _club_member_count(session, club.id) >= club.max_members:
        raise AppError("CLUB_FULL", "This club is full.", status_code=409)
    invite.status = "accepted"
    invite.responded_at = datetime.now(UTC)
    session.add(ClubMembership(club_id=club.id, user_id=user_id, role="member"))
    await record_analytics_event(
        session,
        event_name="social.club_joined",
        user_id=user_id,
        payload={"club_id": str(club.id), "method": "invite"},
    )
    await session.commit()
    return await _club_response(session, club, user_id=user_id)


async def decline_club_invite(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    invite_id: uuid.UUID,
) -> ClubInviteResponse:
    invite = await session.get(ClubInvite, invite_id)
    if invite is None or invite.invitee_user_id != user_id:
        raise AppError("CLUB_INVITE_NOT_FOUND", "Club invite was not found.", status_code=404)
    invite.status = "declined"
    invite.responded_at = datetime.now(UTC)
    club = await session.get(Club, invite.club_id)
    if club is None:
        raise AppError("CLUB_NOT_FOUND", "Club not found.", status_code=404)
    await session.commit()
    return ClubInviteResponse(
        id=invite.id,
        club_id=club.id,
        club_name=club.name,
        inviter_user_id=invite.inviter_user_id,
        invitee_user_id=invite.invitee_user_id,
        status=invite.status,
        created_at=invite.created_at,
        responded_at=invite.responded_at,
    )


async def leave_club(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
) -> dict[str, str]:
    membership = await _require_membership(session, club_id=club_id, user_id=user_id)
    if membership.role == "owner" and await _club_member_count(session, club_id) > 1:
        raise AppError(
            "CLUB_OWNER_CANNOT_LEAVE",
            "Club owner cannot leave while other members remain.",
            status_code=409,
        )
    await session.execute(delete(ClubMembership).where(ClubMembership.id == membership.id))
    await record_analytics_event(
        session,
        event_name="social.club_left",
        user_id=user_id,
        payload={"club_id": str(club_id)},
    )
    await session.commit()
    return {"status": "left"}


async def contribute_to_club(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
    event_key: str,
    amount: int,
    contribution_type: str,
) -> ClubContributionResponse:
    await _require_membership(session, club_id=club_id, user_id=user_id)
    objective = await _weekly_objective(session, club_id)
    existing = await session.scalar(
        select(ClubContribution).where(
            ClubContribution.club_id == club_id,
            ClubContribution.event_key == event_key,
        )
    )
    if existing is not None:
        return ClubContributionResponse(
            id=existing.id,
            event_key=existing.event_key,
            contribution_type=existing.contribution_type,
            amount=existing.amount,
            objective=_objective_response(objective),
            idempotent=True,
        )

    contribution = ClubContribution(
        club_id=club_id,
        objective_id=objective.id,
        user_id=user_id,
        event_key=event_key,
        contribution_type=contribution_type,
        amount=amount,
    )
    session.add(contribution)
    objective.progress_amount = min(objective.target_amount, objective.progress_amount + amount)
    if objective.progress_amount >= objective.target_amount and objective.status != "completed":
        objective.status = "completed"
        objective.completed_at = datetime.now(UTC)
    await record_analytics_event(
        session,
        event_name="social.club_contribution",
        user_id=user_id,
        payload={
            "club_id": str(club_id),
            "objective_id": str(objective.id),
            "amount": amount,
            "contribution_type": contribution_type,
        },
    )
    await session.commit()
    return ClubContributionResponse(
        id=contribution.id,
        event_key=contribution.event_key,
        contribution_type=contribution.contribution_type,
        amount=contribution.amount,
        objective=_objective_response(objective),
    )


async def assist_club_member(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
    receiver_friend_code: str,
    assist_type: str,
) -> ClubAssistResponse:
    await _require_membership(session, club_id=club_id, user_id=user_id)
    receiver_profile = await _profile_by_friend_code(session, receiver_friend_code)
    if receiver_profile.user_id == user_id:
        raise AppError("CLUB_ASSIST_SELF", "You cannot assist yourself.", status_code=409)
    await _require_membership(session, club_id=club_id, user_id=receiver_profile.user_id)
    period_key = _week_key()
    used = int(
        await session.scalar(
            select(func.count())
            .select_from(ClubAssist)
            .where(ClubAssist.helper_user_id == user_id, ClubAssist.period_key == period_key)
        )
        or 0
    )
    if used >= WEEKLY_ASSIST_LIMIT:
        raise AppError("CLUB_ASSIST_LIMIT", "Weekly assist limit reached.", status_code=409)
    existing = await session.scalar(
        select(ClubAssist).where(
            ClubAssist.helper_user_id == user_id,
            ClubAssist.receiver_user_id == receiver_profile.user_id,
            ClubAssist.period_key == period_key,
        )
    )
    if existing is not None:
        raise AppError("CLUB_ASSIST_DUPLICATE", "You already assisted this member this week.", status_code=409)
    assist = ClubAssist(
        club_id=club_id,
        helper_user_id=user_id,
        receiver_user_id=receiver_profile.user_id,
        period_key=period_key,
        assist_type=assist_type,
    )
    session.add(assist)
    await session.flush()
    await contribute_to_club(
        session,
        user_id=user_id,
        club_id=club_id,
        event_key=f"assist:{period_key}:{user_id}:{receiver_profile.user_id}",
        amount=1,
        contribution_type="assist",
    )
    return ClubAssistResponse(
        id=assist.id,
        helper_user_id=user_id,
        receiver_user_id=receiver_profile.user_id,
        period_key=period_key,
        assist_type=assist_type,
        remaining_weekly_assists=max(0, WEEKLY_ASSIST_LIMIT - used - 1),
    )


async def react_in_club(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
    target_type: str,
    target_id: str,
    reaction_key: str,
) -> ClubReactionResponse:
    await _require_membership(session, club_id=club_id, user_id=user_id)
    if reaction_key not in ALLOWED_REACTIONS:
        raise AppError("CLUB_REACTION_UNSUPPORTED", "Unsupported club reaction.", status_code=400)
    existing = await session.scalar(
        select(ClubReaction).where(
            ClubReaction.club_id == club_id,
            ClubReaction.user_id == user_id,
            ClubReaction.target_type == target_type,
            ClubReaction.target_id == target_id,
            ClubReaction.reaction_key == reaction_key,
        )
    )
    if existing is not None:
        return ClubReactionResponse(
            id=existing.id,
            target_type=existing.target_type,
            target_id=existing.target_id,
            reaction_key=existing.reaction_key,
            idempotent=True,
        )
    reaction = ClubReaction(
        club_id=club_id,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        reaction_key=reaction_key,
    )
    session.add(reaction)
    await session.commit()
    return ClubReactionResponse(
        id=reaction.id,
        target_type=reaction.target_type,
        target_id=reaction.target_id,
        reaction_key=reaction.reaction_key,
    )


async def claim_club_reward(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    club_id: uuid.UUID,
) -> ClubRewardClaimResponse:
    await _require_membership(session, club_id=club_id, user_id=user_id)
    objective = await _weekly_objective(session, club_id)
    if objective.status != "completed":
        raise AppError("CLUB_OBJECTIVE_INCOMPLETE", "Club objective is not complete.", status_code=409)
    existing = await session.scalar(
        select(ClubRewardClaim).where(
            ClubRewardClaim.objective_id == objective.id,
            ClubRewardClaim.user_id == user_id,
        )
    )
    wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id).with_for_update())
    if wallet is None:
        raise AppError("PLAYER_STATE_INCOMPLETE", "Player wallet is missing.", status_code=500)
    if existing is not None:
        return ClubRewardClaimResponse(
            club_id=club_id,
            objective_id=objective.id,
            cash=wallet.cash,
            cash_delta=0,
            transaction_id=existing.transaction_id,
            idempotent=True,
        )

    before = wallet.cash
    wallet.cash += objective.reward_cash
    transaction_id = uuid.uuid4()
    claim = ClubRewardClaim(
        objective_id=objective.id,
        club_id=club_id,
        user_id=user_id,
        amount_cash=objective.reward_cash,
        transaction_id=transaction_id,
    )
    session.add(claim)
    session.add(
        EconomyLedger(
            transaction_id=transaction_id,
            user_id=user_id,
            currency="cash",
            amount=objective.reward_cash,
            source_or_sink="club_reward",
            reference_type="club_objective",
            reference_id=str(objective.id),
            config_version=CLUB_CONFIG_VERSION,
            balance_before=before,
            balance_after=wallet.cash,
        )
    )
    await record_analytics_event(
        session,
        event_name="social.club_reward_claimed",
        user_id=user_id,
        payload={"club_id": str(club_id), "objective_id": str(objective.id), "cash_delta": objective.reward_cash},
    )
    await session.commit()
    return ClubRewardClaimResponse(
        club_id=club_id,
        objective_id=objective.id,
        cash=wallet.cash,
        cash_delta=objective.reward_cash,
        transaction_id=transaction_id,
    )
