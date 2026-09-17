"""
Mock AI provider.

Lets the whole application run end-to-end with zero API keys and zero
network calls - useful for local development, demos, and automated tests.

This is intentionally a *simple* rule-based (keyword) classifier. That's
fine for a mock: its only job is to stand in for a real LLM so the rest of
the app (frontend, API, database) can be built and tested without an API
key. The real intelligence lives in the Gemini/OpenAI providers, which
actually understand meaning rather than matching keywords (see section
"AI Classification" in the README for why that distinction matters).
"""
import asyncio
import re
from typing import Any

from app.services.providers.base import AIProvider

# A tiny artificial delay so the frontend's loading state is visible during
# local demos, similar to what a real network call to an LLM would feel like.
MOCK_ARTIFICIAL_DELAY_SECONDS = 0.5

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "plumbing": [
        "leak", "water", "pipe", "faucet", "tap", "drain", "sink", "plumbing", "flood",
        "تسريب", "تسرب", "مويه", "مويّة", "مياه", "ماء", "صنبور", "مواسير", "سباكة", "حنفية", "مجاري",
    ],
    "electrical": [
        "electric", "electricity", "power", "wire", "wiring", "outlet", "socket", "breaker", "short circuit",
        "كهرباء", "كهربائي", "سلك", "أسلاك", "مقبس", "قاطع", "كهرب",
    ],
    "carpentry": [
        "door", "window", "cabinet", "wood", "lock", "furniture", "hinge",
        "باب", "شباك", "نافذة", "خشب", "دولاب", "قفل", "نجارة", "مفصلة",
    ],
    "ac": [
        "ac", "a/c", "air condition", "air conditioner", "cooling", "cool", "compressor",
        "مكيف", "تكييف", "تبريد", "بارد", "يبرد",
    ],
    "insulation": [
        "insulation", "insulate", "waterproofing", "roof leak",
        "عزل", "عازل", "عزل مائي", "عزل حراري",
    ],
    "flooring": [
        "floor", "tile", "flooring", "parquet",
        "أرضية", "ارضيه", "بلاط", "سيراميك", "باركيه",
    ],
}

_URGENT_KEYWORDS = [
    "flooding", "flood", "danger", "dangerous", "hazard", "spark", "sparking", "exposed wire",
    "fire", "smoke", "gas smell", "emergency", "urgent",
    "خطر", "غرق", "غرقان", "شرارة", "ماس كهربائي", "حريق", "دخان", "رائحة غاز", "طارئ", "عاجل",
]

# Splits on English "and" and Arabic "و" used as a conjunction between two
# independent clauses (e.g. "...في المطبخ والكهرباء مقطوعة..."). This is a
# simple heuristic appropriate for a mock/demo classifier - it is NOT meant
# to be a general-purpose Arabic NLP tokenizer.
_SPLIT_PATTERN = re.compile(r"\s+و\s*(?=\S)|\band\b", re.IGNORECASE)

_MIN_SEGMENT_LENGTH = 3


def _split_into_segments(description: str) -> list[str]:
    raw_segments = _SPLIT_PATTERN.split(description)
    segments = [segment.strip(" ,.،؛\n\t") for segment in raw_segments]
    segments = [segment for segment in segments if len(segment) >= _MIN_SEGMENT_LENGTH]
    return segments or [description.strip()]


def _classify_segment(segment: str) -> dict[str, str]:
    lowered = segment.lower()

    category = "other"
    for candidate_category, keywords in _CATEGORY_KEYWORDS.items():
        if any(keyword in lowered or keyword in segment for keyword in keywords):
            category = candidate_category
            break

    is_urgent = any(keyword in lowered or keyword in segment for keyword in _URGENT_KEYWORDS)

    # A water leak is treated as urgent by default (risk of water damage),
    # mirroring the examples in the spec, even without an explicit "danger"
    # keyword in the text.
    if category == "plumbing" and ("leak" in lowered or "تسريب" in segment or "تسرب" in segment):
        is_urgent = True

    priority = "urgent" if is_urgent else "normal"
    return {"problem": segment, "category": category, "priority": priority}


class MockAIProvider(AIProvider):
    name = "mock"

    async def generate(self, description: str) -> dict[str, Any]:
        if MOCK_ARTIFICIAL_DELAY_SECONDS:
            await asyncio.sleep(MOCK_ARTIFICIAL_DELAY_SECONDS)

        segments = _split_into_segments(description)
        requests = [_classify_segment(segment) for segment in segments]
        return {"requests": requests}
