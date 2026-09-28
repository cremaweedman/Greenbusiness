from __future__ import annotations

import uuid

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service import (
    get_player_state,
    login_user,
    register_user,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.config import settings
from app.dependencies import get_current_user_id, get_db
from app.errors import AppError
from app.schemas import LoginRequest, PlayerResponse, RegisterRequest, TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])
player_router = APIRouter(tags=["player"])


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.refresh_ttl_seconds,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.refresh_cookie_name, path="/")


@auth_router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    _, access_token, refresh_token = await register_user(
        session,
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        request_id=getattr(request.state, "request_id", None),
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, expires_in=settings.jwt_access_ttl_seconds)


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    _, access_token, refresh_token = await login_user(
        session,
        email=body.email,
        password=body.password,
        request_id=getattr(request.state, "request_id", None),
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, expires_in=settings.jwt_access_ttl_seconds)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
) -> TokenResponse:
    if not refresh_token:
        raise AppError("AUTH_REFRESH_REQUIRED", "Refresh token is required.", status_code=401)
    _, access_token, replacement = await rotate_refresh_token(
        session,
        refresh_token=refresh_token,
        request_id=getattr(request.state, "request_id", None),
    )
    _set_refresh_cookie(response, replacement)
    return TokenResponse(access_token=access_token, expires_in=settings.jwt_access_ttl_seconds)


@auth_router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
) -> Response:
    await revoke_refresh_token(
        session,
        refresh_token=refresh_token,
        request_id=getattr(request.state, "request_id", None),
    )
    _clear_refresh_cookie(response)
    response.status_code = 204
    return response


@player_router.get("/player", response_model=PlayerResponse)
async def player(
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    return await get_player_state(session, user_id)
