from fastapi import APIRouter

from app.auth_routes import auth_router, player_router
from app.production_routes import production_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(player_router)
router.include_router(production_router)


@router.get("/system/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok", "api_version": "v1"}
