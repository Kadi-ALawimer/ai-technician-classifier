"""
Google Gemini provider.

Talks to the Gemini REST API directly over HTTPS (via httpx) rather than
pulling in the full Google SDK - for a project this size, one small,
transparent HTTP call is easier to read, debug, and explain in a live
review than an extra SDK dependency.

Uses Gemini's structured output feature (responseMimeType +
responseSchema) so the model is constrained to return JSON matching our
schema. We still re-validate everything with Pydantic afterwards
(app/services/ai_service.py) - never trust an external API blindly, even
one that claims to enforce a schema.
"""
import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.providers.base import AIProvider, AIProviderError
from app.services.prompts import RESPONSE_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _to_gemini_schema(node: Any) -> Any:
    """Convert our plain JSON-Schema-style dict into Gemini's Schema format.

    The two differ mainly in that Gemini expects "type" values in uppercase
    (e.g. "OBJECT" instead of "object"). Keeping one schema definition in
    prompts.py and converting it here avoids maintaining two copies that
    could drift apart.
    """
    if not isinstance(node, dict):
        return node

    converted: dict[str, Any] = {}
    for key, value in node.items():
        if key == "type" and isinstance(value, str):
            converted[key] = value.upper()
        elif key == "properties" and isinstance(value, dict):
            converted[key] = {prop_name: _to_gemini_schema(prop_val) for prop_name, prop_val in value.items()}
        elif key == "items":
            converted[key] = _to_gemini_schema(value)
        else:
            converted[key] = value
    return converted


class GeminiAIProvider(AIProvider):
    name = "gemini"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.GEMINI_API_KEY
        self._model = settings.GEMINI_MODEL
        self._timeout = settings.AI_REQUEST_TIMEOUT_SECONDS

    async def generate(self, description: str) -> dict[str, Any]:
        if not self._api_key:
            raise AIProviderError(
                "GEMINI_API_KEY is not configured. Set it in backend/.env or switch "
                "AI_PROVIDER=mock to run without a real AI provider."
            )

        url = f"{GEMINI_API_BASE}/{self._model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": build_user_prompt(description)}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": _to_gemini_schema(RESPONSE_JSON_SCHEMA),
                "temperature": 0.2,
            },
        }
        headers = {"x-goog-api-key": self._api_key, "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.exception("Network error calling Gemini API")
            raise AIProviderError(f"Failed to reach the Gemini API: {exc}") from exc

        if response.status_code != 200:
            logger.error("Gemini API returned status %s: %s", response.status_code, response.text[:500])
            raise AIProviderError(f"Gemini API returned an error (status {response.status_code}).")

        try:
            body = response.json()
            text = body["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.exception("Unexpected Gemini API response shape: %s", response.text[:500])
            raise AIProviderError("Gemini API returned an unexpected response shape.") from exc

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.exception("Gemini API did not return valid JSON: %s", text[:500])
            raise AIProviderError("Gemini API did not return valid JSON.") from exc
