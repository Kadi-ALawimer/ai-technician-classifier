"""
Pydantic schemas (API contracts).

These are deliberately separate from the SQLModel database model
(app.models.request.Request) even though SQLModel *could* let us reuse one
class for both. Keeping them separate means the API's input/output shape
can evolve independently from the storage shape, and it makes the
validation rules for each endpoint explicit and easy to find.
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.config import get_settings
from app.models.enums import Category, Priority

settings = get_settings()


# ---------------------------------------------------------------------------
# POST /api/analyze
# ---------------------------------------------------------------------------
class AnalyzeRequestIn(BaseModel):
    """Input payload for the AI analysis endpoint."""

    description: str = Field(
        ...,
        description="Free-text description of one or more problems, in Arabic or English.",
    )

    @field_validator("description")
    @classmethod
    def description_must_be_reasonable(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < settings.MIN_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description must be at least {settings.MIN_DESCRIPTION_LENGTH} characters long."
            )
        if len(cleaned) > settings.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description must be at most {settings.MAX_DESCRIPTION_LENGTH} characters long."
            )
        return cleaned


class ClassifiedProblem(BaseModel):
    """One independent problem extracted from the user's description."""

    problem: str = Field(..., min_length=1, max_length=500)
    category: Category
    priority: Priority


class AnalyzeResponseOut(BaseModel):
    requests: list[ClassifiedProblem]


# ---------------------------------------------------------------------------
# POST /api/requests
# ---------------------------------------------------------------------------
class RequestCreateIn(BaseModel):
    """Payload to persist a single (possibly user-edited) request."""

    problem: str = Field(
        ...,
        min_length=settings.MIN_PROBLEM_LENGTH,
        max_length=settings.MAX_PROBLEM_LENGTH,
    )
    category: Category
    priority: Priority

    @field_validator("problem")
    @classmethod
    def problem_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Problem text cannot be empty.")
        return cleaned


# ---------------------------------------------------------------------------
# GET /api/requests, response for POST /api/requests
# ---------------------------------------------------------------------------
class RequestOut(BaseModel):
    id: int
    problem: str
    category: Category
    priority: Priority
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------
class HealthOut(BaseModel):
    status: str
    ai_provider: str


# ---------------------------------------------------------------------------
# Generic error envelope returned to the frontend (never a raw stack trace)
# ---------------------------------------------------------------------------
class ErrorOut(BaseModel):
    detail: str
