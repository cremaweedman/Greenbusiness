import asyncio
import hashlib
import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import router as v1_router
from app.config import settings
from app.db.session import SessionLocal, engine
from app.errors import AppError, app_error_handler
from app.liveops_service import record_analytics_event
from app.rate_limit import RateLimitExceeded, RateLimitRule, enforce_rate_limit
from app.security_events import security_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("greenbusiness.api")
_analytics_tasks: set[asyncio.Task[None]] = set()

app = FastAPI(title="GreenBusiness API", version="0.9.0")
app.add_exception_handler(AppError, app_error_handler)
app.include_router(v1_router)

_RATE_LIMITS: tuple[tuple[str, str, RateLimitRule], ...] = (
    ("POST", "/v1/auth/register", RateLimitRule("auth-register", 12, 60)),
    ("POST", "/v1/auth/login", RateLimitRule("auth-login", 15, 60)),
    ("POST", "/v1/auth/refresh", RateLimitRule("auth-refresh", 45, 60)),
    ("POST", "/v1/auth/dev/creator", RateLimitRule("creator-access", 5, 60)),
    ("POST", "/v1/admin/auth/token", RateLimitRule("admin-bootstrap", 8, 60)),
    ("POST", "/v1/store/purchases/validate", RateLimitRule("store-purchase", 20, 60)),
    ("POST", "/v1/store/rewarded-ads/claim", RateLimitRule("rewarded-ad", 20, 60)),
    ("POST", "/v1/social/friends/redeem", RateLimitRule("friend-code-redeem", 20, 60)),
    ("POST", "/v1/clubs/join", RateLimitRule("club-code-join", 20, 60)),
)


def _rate_rule(request: Request) -> RateLimitRule | None:
    method = request.method.upper()
    path = request.url.path
    for expected_method, expected_path, rule in _RATE_LIMITS:
        if method == expected_method and path == expected_path:
            return rule
    if (
        method == "POST"
        and path.startswith("/v1/store/purchases/")
        and path.endswith("/refund")
    ):
        return RateLimitRule("store-refund", 10, 60)
    if path.startswith("/v1/admin/"):
        return RateLimitRule("admin-api", 120, 60)
    if path.startswith(("/v1/social/", "/v1/clubs/")):
        return RateLimitRule("social-api", 120, 60)
    return None


def _rate_subject(request: Request) -> str:
    auth = request.headers.get("authorization")
    if auth:
        return "auth:" + hashlib.sha256(auth.encode("utf-8")).hexdigest()[:24]
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return "ip:" + real_ip
    if request.client is not None:
        return "ip:" + request.client.host
    return "ip:unknown"


def _security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    )
    if settings.production_like:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def security_and_request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()

    rule = _rate_rule(request)
    if rule is not None:
        try:
            await enforce_rate_limit(rule, subject=_rate_subject(request))
        except RateLimitExceeded as exc:
            security_event(
                "abuse.rate_limit_exceeded",
                scope=rule.scope,
                method=request.method,
                path=request.url.path,
                request_id=request_id,
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests.",
                    }
                },
                headers={"Retry-After": str(exc.retry_after), "X-Request-ID": request_id},
            )
            return _security_headers(response)

    try:
        response = await call_next(request)
    except Exception:
        await _record_request_analytics(
            request,
            request_id=request_id,
            status_code=500,
            duration_ms=(time.perf_counter() - start) * 1000,
            failed=True,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        await _record_request_analytics(
            request,
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=duration_ms,
            failed=True,
        )
    elif _sample_success_request(request_id):
        task = asyncio.create_task(
            _record_request_analytics(
                request,
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=duration_ms,
                failed=False,
                apply_sampling=False,
            )
        )
        _analytics_tasks.add(task)
        task.add_done_callback(_analytics_tasks.discard)
    response.headers["X-Request-ID"] = request_id
    return _security_headers(response)


def _sample_success_request(request_id: str) -> bool:
    rate = settings.analytics_request_sample_rate
    if rate >= 1:
        return True
    if rate <= 0:
        return False
    value = int(hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:8], 16)
    return value / 0xFFFFFFFF <= rate


async def _record_request_analytics(
    request: Request,
    *,
    request_id: str,
    status_code: int,
    duration_ms: float,
    failed: bool,
    apply_sampling: bool = True,
) -> None:
    if request.url.path.startswith("/health"):
        return
    if apply_sampling and not failed and not _sample_success_request(request_id):
        return

    payload = {
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    try:
        async with SessionLocal() as session:
            await record_analytics_event(
                session,
                event_name="performance.api_request_completed",
                payload=payload,
                request_id=request_id,
            )
            if failed:
                await record_analytics_event(
                    session,
                    event_name="errors.api_request_failed",
                    payload=payload,
                    request_id=request_id,
                )
            await session.commit()
    except Exception:
        logger.debug("request analytics capture skipped", exc_info=True)


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception:
        logger.exception("readiness check failed")
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "error"})
