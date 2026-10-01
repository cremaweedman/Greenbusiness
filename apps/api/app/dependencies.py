from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

import jwt
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service import decode_user_id
from app.config import settings
from app.db.session import SessionLocal
from app.errors import AppError
from app.security import (
    AdminPrincipal,
    decode_admin_access_token,
    require_admin_role,
    verify_admin_bootstrap_key,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_current_user_id(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("AUTH_REQUIRED", "Authentication required.", status_code=401)
    return decode_user_id(authorization[7:].strip())


async def get_admin_bootstrap_principal(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> AdminPrincipal:
    try:
        return verify_admin_bootstrap_key(x_admin_key)
    except jwt.InvalidTokenError as exc:
        raise AppError("ADMIN_AUTH_REQUIRED", "Admin authentication required.", status_code=401) from exc


async def get_admin_principal(
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> AdminPrincipal:
    if authorization and authorization.startswith("Bearer "):
        try:
            return decode_admin_access_token(authorization[7:].strip())
        except jwt.InvalidTokenError as exc:
            raise AppError("ADMIN_AUTH_REQUIRED", "Admin authentication required.", status_code=401) from exc

    if settings.app_env.lower() in {"development", "local", "test"}:
        try:
            return verify_admin_bootstrap_key(x_admin_key)
        except jwt.InvalidTokenError:
            pass

    raise AppError("ADMIN_AUTH_REQUIRED", "Admin authentication required.", status_code=401)


AdminPrincipalDep = Annotated[AdminPrincipal, Depends(get_admin_principal)]


async def get_admin_actor_id(principal: AdminPrincipalDep) -> str:
    return principal.actor_id


async def get_admin_operator_id(principal: AdminPrincipalDep) -> str:
    try:
        require_admin_role(principal, minimum="operator")
    except jwt.InvalidTokenError as exc:
        raise AppError("ADMIN_FORBIDDEN", "Admin operator role required.", status_code=403) from exc
    return principal.actor_id
