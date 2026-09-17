"""
Shared pytest fixtures.

Two important things happen here:
1. Environment variables are forced to safe test values (AI_PROVIDER=mock,
   an in-memory database) BEFORE any `app.*` module is imported. Settings
   are cached (see app.core.config.get_settings), so this must happen
   first - it's why these lines sit above the `from app...` imports below,
   which normally would trigger a lint warning but is required here.
2. The database dependency (get_session) is overridden with a fresh,
   isolated in-memory SQLite session per test, so tests never touch a real
   app.db file and never leak state between tests.
"""
import os

os.environ["AI_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402

from app.database.db import get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
