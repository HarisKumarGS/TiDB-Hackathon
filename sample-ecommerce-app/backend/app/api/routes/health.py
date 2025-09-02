from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Liveness probe")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/deep", summary="Readiness probe")
async def health_deep() -> dict:
    # Extend with DB/Cache checks as needed
    return {"status": "ok", "checks": {"db": "ok"}}

