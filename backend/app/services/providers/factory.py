"""
Provider factory.

Reads AI_PROVIDER from settings and returns the matching provider
instance. This is the ONLY place in the codebase that branches on which
provider is configured - everything else (routes, ai_service) works
against the generic AIProvider interface. Adding a new provider later
means: implement AIProvider, add one line here.
"""
from app.core.config import get_settings
from app.services.providers.base import AIProvider
from app.services.providers.gemini_provider import GeminiAIProvider
from app.services.providers.mock_provider import MockAIProvider
from app.services.providers.openai_provider import OpenAIAIProvider

_PROVIDERS: dict[str, type[AIProvider]] = {
    "mock": MockAIProvider,
    "gemini": GeminiAIProvider,
    "openai": OpenAIAIProvider,
}


def get_provider() -> AIProvider:
    settings = get_settings()
    provider_key = settings.AI_PROVIDER.strip().lower()
    provider_class = _PROVIDERS.get(provider_key)
    if provider_class is None:
        raise ValueError(
            f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}'. "
            f"Valid options are: {', '.join(_PROVIDERS.keys())}."
        )
    return provider_class()
