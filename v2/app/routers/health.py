"""Роутер: проверка работоспособности сервиса."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas import HealthOut
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
async def health():
    db_ok, payload = await HealthService().check()
    if not db_ok:
        return JSONResponse(status_code=503, content=payload.model_dump())
    return payload
