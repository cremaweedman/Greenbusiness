import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import router as v1_router
from app.db.session import SessionLocal, engine
from app.errors import AppError, app_error_handler
from app.liveops_service import record_analytics_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("greenbusiness.api")

app = FastAPI(title="GreenBusiness API", version="0.2.0")
app.add_exception_handler(AppError, app_error_handler)
app.include_router(v1_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
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
    await _record_request_analytics(
        request,
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=duration_ms,
        failed=response.status_code >= 400,
    )
    response.headers["X-Request-ID"] = request_id
    return response


async def _record_request_analytics(
    request: Request,
    *,
    request_id: str,
    status_code: int,
    duration_ms: float,
    failed: bool,
) -> None:
    if request.url.path.startswith("/health"):
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
