from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service import decode_user_id
from app.config import settings
from app.db.session import SessionLocal
from app.errors import AppError


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


async def get_admin_actor_id(x_admin_key: str | None = Header(default=None)) -> str:
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise AppError("ADMIN_AUTH_REQUIRED", "Admin authentication required.", status_code=401)
    return "admin-api"
