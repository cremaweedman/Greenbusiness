from fastapi import APIRouter

from app.auth_routes import auth_router, player_router
from app.contracts_routes import contracts_router
from app.economy_routes import economy_router
from app.production_routes import production_router
from app.skills_routes import skills_router
from app.upgrades_routes import upgrades_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(player_router)
router.include_router(production_router)
router.include_router(contracts_router)
router.include_router(economy_router)
router.include_router(upgrades_router)
router.include_router(skills_router)


@router.get("/system/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok", "api_version": "v1"}
