from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user_id, get_db
from app.liveops_service import require_feature_enabled
from app.schemas import (
    ClubAssistRequest,
    ClubAssistResponse,
    ClubContributionRequest,
    ClubContributionResponse,
    ClubCreateRequest,
    ClubInviteCreateRequest,
    ClubInviteResponse,
    ClubJoinRequest,
    ClubReactionRequest,
    ClubReactionResponse,
    ClubResponse,
    ClubRewardClaimResponse,
    FriendRedeemRequest,
    FriendResponse,
    SocialProfileResponse,
    SocialStateResponse,
)
from app.social_service import (
    accept_club_invite,
    assist_club_member,
    claim_club_reward,
    contribute_to_club,
    create_club,
    create_club_invite,
    decline_club_invite,
    join_club_by_invite_code,
    leave_club,
    list_friends,
    react_in_club,
    redeem_friend_code,
    social_profile_response,
    social_state,
)

social_router = APIRouter(prefix="/social", tags=["social"])
clubs_router = APIRouter(prefix="/clubs", tags=["clubs"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]


async def _clubs_enabled(session: AsyncSession) -> None:
    await require_feature_enabled(session, "clubs")


@social_router.get("/me", response_model=SocialStateResponse)
async def get_social_state(
    user_id: CurrentUserId,
    session: DbSession,
) -> SocialStateResponse:
    await _clubs_enabled(session)
    response = await social_state(session, user_id)
    await session.commit()
    return response


@social_router.get("/profile", response_model=SocialProfileResponse)
async def get_social_profile(
    user_id: CurrentUserId,
    session: DbSession,
) -> SocialProfileResponse:
    await _clubs_enabled(session)
    response = await social_profile_response(session, user_id)
    await session.commit()
    return response


@social_router.get("/friends", response_model=list[FriendResponse])
async def get_friends(
    user_id: CurrentUserId,
    session: DbSession,
) -> list[FriendResponse]:
    await _clubs_enabled(session)
    return await list_friends(session, user_id)


@social_router.post("/friends/redeem", response_model=FriendResponse)
async def redeem_friend(
    body: FriendRedeemRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> FriendResponse:
    await _clubs_enabled(session)
    response = await redeem_friend_code(session, user_id=user_id, friend_code=body.friend_code)
    await session.commit()
    return response


@clubs_router.post("", response_model=ClubResponse, status_code=201)
async def create_player_club(
    body: ClubCreateRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubResponse:
    await _clubs_enabled(session)
    return await create_club(session, user_id=user_id, name=body.name)


@clubs_router.post("/join", response_model=ClubResponse)
async def join_player_club(
    body: ClubJoinRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubResponse:
    await _clubs_enabled(session)
    return await join_club_by_invite_code(session, user_id=user_id, invite_code=body.invite_code)


@clubs_router.post("/{club_id}/leave")
async def leave_player_club(
    club_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict[str, str]:
    await _clubs_enabled(session)
    return await leave_club(session, user_id=user_id, club_id=club_id)


@clubs_router.post("/{club_id}/invites", response_model=ClubInviteResponse, status_code=201)
async def invite_player_to_club(
    club_id: uuid.UUID,
    body: ClubInviteCreateRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubInviteResponse:
    await _clubs_enabled(session)
    return await create_club_invite(
        session,
        user_id=user_id,
        club_id=club_id,
        friend_code=body.friend_code,
    )


@clubs_router.post("/invites/{invite_id}/accept", response_model=ClubResponse)
async def accept_player_club_invite(
    invite_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubResponse:
    await _clubs_enabled(session)
    return await accept_club_invite(session, user_id=user_id, invite_id=invite_id)


@clubs_router.post("/invites/{invite_id}/decline", response_model=ClubInviteResponse)
async def decline_player_club_invite(
    invite_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubInviteResponse:
    await _clubs_enabled(session)
    return await decline_club_invite(session, user_id=user_id, invite_id=invite_id)


@clubs_router.post("/{club_id}/contributions", response_model=ClubContributionResponse)
async def add_club_contribution(
    club_id: uuid.UUID,
    body: ClubContributionRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubContributionResponse:
    await _clubs_enabled(session)
    return await contribute_to_club(
        session,
        user_id=user_id,
        club_id=club_id,
        event_key=body.event_key,
        amount=body.amount,
        contribution_type=body.contribution_type,
    )


@clubs_router.post("/{club_id}/assists", response_model=ClubAssistResponse)
async def assist_player_in_club(
    club_id: uuid.UUID,
    body: ClubAssistRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubAssistResponse:
    await _clubs_enabled(session)
    return await assist_club_member(
        session,
        user_id=user_id,
        club_id=club_id,
        receiver_friend_code=body.receiver_friend_code,
        assist_type=body.assist_type,
    )


@clubs_router.post("/{club_id}/reactions", response_model=ClubReactionResponse)
async def add_club_reaction(
    club_id: uuid.UUID,
    body: ClubReactionRequest,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubReactionResponse:
    await _clubs_enabled(session)
    return await react_in_club(
        session,
        user_id=user_id,
        club_id=club_id,
        target_type=body.target_type,
        target_id=body.target_id,
        reaction_key=body.reaction_key,
    )


@clubs_router.post("/{club_id}/rewards/claim", response_model=ClubRewardClaimResponse)
async def claim_player_club_reward(
    club_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> ClubRewardClaimResponse:
    await _clubs_enabled(session)
    return await claim_club_reward(session, user_id=user_id, club_id=club_id)
