"""
OpenAI provider.

Talks to the OpenAI Chat Completions REST API directly over HTTPS (via
httpx), using OpenAI's Structured Outputs feature (response_format =
json_schema, strict mode) so the model is constrained to return JSON that
matches our schema exactly. As with the Gemini provider, the response is
still independently re-validated with Pydantic afterwards - see
app/services/ai_service.py.
"""
import copy
import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.providers.base import AIProvider, AIProviderError
from app.services.prompts import RESPONSE_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"


def _to_strict_json_schema(node: Any) -> Any:
    """Add the constraints OpenAI's Structured Outputs "strict" mode requires.

    Strict mode needs every object to set additionalProperties=false and
    list every property in "required". We derive this automatically from
    our base schema instead of hand-maintaining a second copy.
    """
    if isinstance(node, list):
        return [_to_strict_json_schema(item) for item in node]
    if not isinstance(node, dict):
        return node

    converted = {key: _to_strict_json_schema(value) for key, value in node.items()}
    if converted.get("type") == "object":
        converted["additionalProperties"] = False
        if "properties" in converted:
            converted["required"] = list(converted["properties"].keys())
    return converted


class OpenAIAIProvider(AIProvider):
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.OPENAI_API_KEY
        self._model = settings.OPENAI_MODEL
        self._timeout = settings.AI_REQUEST_TIMEOUT_SECONDS

    async def generate(self, description: str) -> dict[str, Any]:
        if not self._api_key:
            raise AIProviderError(
                "OPENAI_API_KEY is not configured. Set it in backend/.env or switch "
                "AI_PROVIDER=mock to run without a real AI provider."
            )

        payload = {
            "model": self._model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(description)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "technician_requests",
                    "schema": _to_strict_json_schema(copy.deepcopy(RESPONSE_JSON_SCHEMA)),
                    "strict": True,
                },
            },
        }
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(OPENAI_CHAT_COMPLETIONS_URL, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.exception("Network error calling OpenAI API")
            raise AIProviderError(f"Failed to reach the OpenAI API: {exc}") from exc

        if response.status_code != 200:
            logger.error("OpenAI API returned status %s: %s", response.status_code, response.text[:500])
            raise AIProviderError(f"OpenAI API returned an error (status {response.status_code}).")

        try:
            body = response.json()
            text = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.exception("Unexpected OpenAI API response shape: %s", response.text[:500])
            raise AIProviderError("OpenAI API returned an unexpected response shape.") from exc

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.exception("OpenAI API did not return valid JSON: %s", text[:500])
            raise AIProviderError("OpenAI API did not return valid JSON.") from exc
