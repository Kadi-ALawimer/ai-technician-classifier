"""
Provider interface.

Every AI provider (mock, Gemini, OpenAI, ...) implements this same tiny
interface: given a description, return a raw dict that *should* match the
{"requests": [...]} shape. The caller (ai_service.py) is responsible for
validating that shape - providers are only responsible for talking to
their backend and returning parsed JSON.

This is what makes swapping providers a one-line change (AI_PROVIDER in
.env) instead of a rewrite: nothing else in the codebase depends on which
provider is active.
"""
from abc import ABC, abstractmethod
from typing import Any


class AIProviderError(Exception):
    """Raised when a provider fails to produce a usable response.

    This covers network failures, missing API keys, non-2xx responses from
    the LLM API, and responses that aren't valid JSON at all. It is caught
    in the API layer and turned into a clean, user-facing error message -
    the raw exception/stack trace is never sent to the frontend.
    """


class AIProvider(ABC):
    """Abstract base class all AI providers must implement."""

    name: str = "base"

    @abstractmethod
    async def generate(self, description: str) -> dict[str, Any]:
        """Return a parsed JSON object (as a Python dict) for the given description.

        Implementations should raise AIProviderError for any failure
        (network error, bad status code, invalid JSON). They should NOT
        attempt to validate the business schema (category/priority
        enums etc.) - that's ai_service.py's job.
        """
        raise NotImplementedError
