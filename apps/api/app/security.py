from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.config import settings

_password_hasher = PasswordHasher()


@dataclass(frozen=True)
class AdminPrincipal:
    actor_id: str
    role: str


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: uuid.UUID) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_access_ttl_seconds),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> uuid.UUID:
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        options={"require": ["sub", "type", "iss", "iat", "exp", "jti"]},
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("invalid token type")
    return uuid.UUID(str(payload["sub"]))


def verify_admin_bootstrap_key(candidate: str | None) -> AdminPrincipal:
    if not candidate or not settings.admin_api_key:
        raise jwt.InvalidTokenError("admin bootstrap key missing")
    if not secrets.compare_digest(candidate, settings.admin_api_key):
        raise jwt.InvalidTokenError("admin bootstrap key invalid")
    return AdminPrincipal(actor_id=settings.admin_actor_id, role=settings.admin_role)


def _admin_jwt_secret() -> str:
    return settings.admin_jwt_secret or settings.jwt_secret


def create_admin_access_token(principal: AdminPrincipal) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": principal.actor_id,
        "role": principal.role,
        "type": "admin_access",
        "iss": f"{settings.jwt_issuer}-admin",
        "iat": now,
        "exp": now + timedelta(seconds=settings.admin_token_ttl_seconds),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _admin_jwt_secret(), algorithm="HS256")


def decode_admin_access_token(token: str) -> AdminPrincipal:
    payload = jwt.decode(
        token,
        _admin_jwt_secret(),
        algorithms=["HS256"],
        issuer=f"{settings.jwt_issuer}-admin",
        options={"require": ["sub", "role", "type", "iss", "iat", "exp", "jti"]},
    )
    if payload.get("type") != "admin_access":
        raise jwt.InvalidTokenError("invalid admin token type")
    role = str(payload["role"])
    if role not in {"viewer", "operator", "superadmin"}:
        raise jwt.InvalidTokenError("invalid admin role")
    return AdminPrincipal(actor_id=str(payload["sub"]), role=role)


def require_admin_role(principal: AdminPrincipal, *, minimum: str) -> None:
    ranks = {"viewer": 1, "operator": 2, "superadmin": 3}
    if ranks.get(principal.role, 0) < ranks[minimum]:
        raise jwt.InvalidTokenError("insufficient admin role")
