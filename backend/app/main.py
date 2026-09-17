"""
FastAPI application entry point.

Wires together configuration, logging, the database, CORS, and the API
routes. Run with:

    uvicorn app.main:app --reload

(from inside the backend/ directory, with the virtual environment active).
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.database.db import create_db_and_tables

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates the SQLite file and tables automatically on first run.
    create_db_and_tables()
    logger.info("%s started | AI_PROVIDER=%s", settings.APP_NAME, settings.AI_PROVIDER)
    yield
    logger.info("%s shutting down", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="Classifies free-text technician service requests using an LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS is restricted to the known local frontend origin(s) - see
# README "Security Considerations" for why we deliberately avoid "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort safety net: never leak a raw stack trace to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": f"{settings.APP_NAME} API. See /docs for interactive API documentation."}
