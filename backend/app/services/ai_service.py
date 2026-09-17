"""
AI service - the single entry point the API layer calls for classification.

This module deliberately contains NO provider-specific code (no HTTP
calls, no SDKs). Its only responsibilities are:
  1. Ask the configured provider (mock/gemini/openai) for a raw response.
  2. Strictly validate that response against our schema with Pydantic.
  3. Raise a single, clean exception type (AIServiceError) the API layer
     can catch and turn into a proper HTTP error - never leaking a raw
     provider error or a stack trace to the frontend.

Routes never talk to a provider directly - they call analyze_request()
from here. That indirection is what makes it trivial to, for example, add
caching, retries, or logging around every provider call in one place.
"""
import logging

from pydantic import ValidationError

from app.schemas.request import AnalyzeResponseOut
from app.services.providers.base import AIProviderError
from app.services.providers.factory import get_provider

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when classification fails for any reason (network, bad
    provider output, invalid JSON shape, etc). Carries a short,
    user-safe message - never a raw stack trace."""


async def analyze_request(description: str) -> AnalyzeResponseOut:
    """Classify a free-text description into one or more structured requests.

    Raises AIServiceError if the provider fails or returns something that
    doesn't match our expected schema. Callers can treat this as the only
    failure mode they need to handle.
    """
    provider = get_provider()

    try:
        raw_result = await provider.generate(description)
    except AIProviderError as exc:
        logger.warning("AI provider '%s' failed: %s", provider.name, exc)
        raise AIServiceError(str(exc)) from exc

    try:
        validated = AnalyzeResponseOut.model_validate(raw_result)
    except ValidationError as exc:
        # This is the important safety net: even if a provider ignores our
        # instructions (wrong category name, missing field, extra field,
        # malformed shape), invalid data never reaches the frontend or the
        # database. We log the details for debugging but return a generic,
        # user-safe message.
        logger.error("AI provider '%s' returned an invalid schema: %s", provider.name, exc)
        raise AIServiceError(
            "The AI returned a response that didn't match the expected format. Please try again."
        ) from exc

    if not validated.requests:
        logger.warning("AI provider '%s' returned zero requests for a non-empty description", provider.name)
        raise AIServiceError("The AI could not identify any problem in the text provided.")

    return validated
