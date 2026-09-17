"""POST /api/analyze - classify a free-text description with the AI service."""
import logging

from fastapi import APIRouter, HTTPException

from app.schemas.request import AnalyzeRequestIn, AnalyzeResponseOut
from app.services.ai_service import AIServiceError, analyze_request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponseOut,
    summary="Classify a problem description into one or more structured requests",
)
async def analyze(payload: AnalyzeRequestIn) -> AnalyzeResponseOut:
    # Pydantic has already validated payload.description (length, not blank)
    # via AnalyzeRequestIn - see app/schemas/request.py.
    try:
        return await analyze_request(payload.description)
    except AIServiceError as exc:
        # 502 Bad Gateway: our server is fine, but the upstream AI provider
        # failed or returned something unusable. The message is safe to
        # show directly to the user (no internals/stack trace).
        raise HTTPException(status_code=502, detail=str(exc)) from exc
