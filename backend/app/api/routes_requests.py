"""POST /api/requests and GET /api/requests - persist and list saved requests."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from app.database.db import get_session
from app.models.request import Request as RequestModel
from app.schemas.request import RequestCreateIn, RequestOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/requests",
    response_model=RequestOut,
    status_code=201,
    summary="Save a (possibly user-edited) classified request",
)
def create_request(payload: RequestCreateIn, session: Session = Depends(get_session)) -> RequestModel:
    # payload.category / payload.priority are already restricted to the
    # Category/Priority enums by Pydantic - an invalid value never reaches
    # this point (FastAPI returns 422 automatically before the handler runs).
    db_request = RequestModel(
        problem=payload.problem,
        category=payload.category,
        priority=payload.priority,
    )
    try:
        session.add(db_request)
        session.commit()
        session.refresh(db_request)
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Database error while saving a request")
        raise HTTPException(status_code=500, detail="Failed to save the request. Please try again.")
    return db_request


@router.get(
    "/requests",
    response_model=list[RequestOut],
    summary="List all saved requests, newest first",
)
def list_requests(session: Session = Depends(get_session)) -> list[RequestModel]:
    try:
        statement = select(RequestModel).order_by(RequestModel.created_at.desc())
        return list(session.exec(statement).all())
    except SQLAlchemyError:
        logger.exception("Database error while listing requests")
        raise HTTPException(status_code=500, detail="Failed to load requests. Please try again.")
