from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service import decode_user_id
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
