"""Aggregates all API routers under the single /api prefix."""
from fastapi import APIRouter

from app.api import routes_analyze, routes_health, routes_requests

api_router = APIRouter(prefix="/api")
api_router.include_router(routes_health.router, tags=["health"])
api_router.include_router(routes_analyze.router, tags=["analyze"])
api_router.include_router(routes_requests.router, tags=["requests"])
