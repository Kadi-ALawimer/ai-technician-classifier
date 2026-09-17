"""
Database engine and session management.

Uses SQLite via SQLModel/SQLAlchemy. The database file and its parent
directory are created automatically on startup if they don't exist yet
(see create_db_and_tables), so there is no manual migration step needed
for this project's scope.
"""
import logging
import os
from typing import Iterator

from sqlmodel import SQLModel, Session, create_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# SQLite needs this connect_arg when used with FastAPI's threaded request
# handling (multiple requests may touch the same connection pool).
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def _ensure_sqlite_directory_exists() -> None:
    """If using a file-based SQLite DB, make sure its parent folder exists."""
    if not settings.DATABASE_URL.startswith("sqlite:///"):
        return
    db_path = settings.DATABASE_URL.replace("sqlite:///", "", 1)
    if db_path in (":memory:", ""):
        return
    parent = os.path.dirname(db_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def create_db_and_tables() -> None:
    """Create the SQLite file and all tables if they don't already exist."""
    _ensure_sqlite_directory_exists()
    SQLModel.metadata.create_all(engine)
    logger.info("Database ready at %s", settings.DATABASE_URL)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
