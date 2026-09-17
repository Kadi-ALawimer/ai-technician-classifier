"""
Tests for POST /api/analyze (AI classification), run against the mock
provider so they are fast, free, and deterministic (no network/API key
required).
"""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ai_provider"] == "mock"


def test_analyze_single_plumbing_problem_is_urgent(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"description": "water leak in kitchen"})
    assert response.status_code == 200

    body = response.json()
    assert len(body["requests"]) == 1
    assert body["requests"][0]["category"] == "plumbing"
    assert body["requests"][0]["priority"] == "urgent"


def test_analyze_ac_problem_is_normal(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"description": "AC is not cooling"})
    assert response.status_code == 200

    body = response.json()
    assert len(body["requests"]) == 1
    assert body["requests"][0]["category"] == "ac"
    assert body["requests"][0]["priority"] == "normal"


def test_analyze_splits_multiple_independent_problems(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"description": "water leak in kitchen and electricity is out in bedroom"},
    )
    assert response.status_code == 200

    body = response.json()
    requests = body["requests"]
    assert len(requests) == 2

    categories = {req["category"] for req in requests}
    assert categories == {"plumbing", "electrical"}

    # Every returned item must respect the fixed vocabularies - this is the
    # contract the frontend and database rely on.
    for req in requests:
        assert req["category"] in [
            "plumbing", "electrical", "carpentry", "ac", "insulation", "flooring", "other",
        ]
        assert req["priority"] in ["normal", "urgent"]


def test_analyze_splits_arabic_multiple_problems(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"description": "عندي تسريب مويه في المطبخ والكهرباء مقطوعة في غرفة النوم"},
    )
    assert response.status_code == 200

    body = response.json()
    requests = body["requests"]
    assert len(requests) == 2
    categories = {req["category"] for req in requests}
    assert categories == {"plumbing", "electrical"}


def test_analyze_rejects_empty_description(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"description": ""})
    assert response.status_code == 422


def test_analyze_rejects_too_short_description(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"description": "a"})
    assert response.status_code == 422


def test_analyze_rejects_missing_field(client: TestClient) -> None:
    response = client.post("/api/analyze", json={})
    assert response.status_code == 422


def test_analyze_response_never_contains_invalid_category(client: TestClient) -> None:
    """
    Guards the "structured output" contract described in the README: no
    matter what free text comes in, every classified item must use one of
    the fixed category/priority values - never something invented.
    """
    response = client.post(
        "/api/analyze",
        json={"description": "the roof is making a strange noise and I don't know why"},
    )
    assert response.status_code == 200
    body = response.json()
    for req in body["requests"]:
        assert req["category"] in [
            "plumbing", "electrical", "carpentry", "ac", "insulation", "flooring", "other",
        ]
        assert req["priority"] in ["normal", "urgent"]
