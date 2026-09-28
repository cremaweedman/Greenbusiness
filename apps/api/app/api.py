from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/system/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok", "api_version": "v1"}
