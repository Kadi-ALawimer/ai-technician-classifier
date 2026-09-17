"""
Database model for a saved technician request.

We use SQLModel because it lets a single class double as both the
SQLAlchemy table definition and a Pydantic model - useful for a small
project like this where we don't want to hand-maintain two parallel
class hierarchies (an ORM model + a schema) for the same entity.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.enums import Category, Priority


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Request(SQLModel, table=True):
    """A single technician service request stored in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    problem: str = Field(nullable=False, max_length=500)
    category: Category = Field(nullable=False, index=True)
    priority: Priority = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False, index=True)
