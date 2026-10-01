from fastapi import APIRouter

from app.admin_routes import admin_router, liveops_router
from app.auth_routes import auth_router, player_router
from app.economy_routes import economy_router
from app.monetization_routes import store_router
from app.production_routes import production_router
from app.social_routes import clubs_router, social_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(player_router)
router.include_router(production_router)
router.include_router(economy_router)
router.include_router(social_router)
router.include_router(clubs_router)
router.include_router(store_router)
router.include_router(liveops_router)
router.include_router(admin_router)


@router.get("/system/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok", "api_version": "v1"}
