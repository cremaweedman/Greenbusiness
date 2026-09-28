import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import router as v1_router
from app.db.session import engine
from app.errors import AppError, app_error_handler


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("greenbusiness.api")

app = FastAPI(title="GreenBusiness API", version="0.2.0")
app.add_exception_handler(AppError, app_error_handler)
app.include_router(v1_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


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
