"""GET /api/health - simple liveness check used by the frontend and by ops."""
from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.request import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut, summary="Health check")
def health() -> HealthOut:
    settings = get_settings()
    return HealthOut(status="ok", ai_provider=settings.AI_PROVIDER)
