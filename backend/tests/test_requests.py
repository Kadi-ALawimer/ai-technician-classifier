"""Tests for POST /api/requests and GET /api/requests (persistence layer)."""
from fastapi.testclient import TestClient


def test_get_requests_starts_empty(client: TestClient) -> None:
    response = client.get("/api/requests")
    assert response.status_code == 200
    assert response.json() == []


def test_create_request_success(client: TestClient) -> None:
    payload = {"problem": "Kitchen sink is leaking", "category": "plumbing", "priority": "urgent"}
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["problem"] == payload["problem"]
    assert body["category"] == "plumbing"
    assert body["priority"] == "urgent"
    assert "id" in body
    assert "created_at" in body


def test_created_request_appears_in_list(client: TestClient) -> None:
    client.post(
        "/api/requests",
        json={"problem": "AC not cooling", "category": "ac", "priority": "normal"},
    )
    response = client.get("/api/requests")
    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "ac"


def test_requests_are_returned_newest_first(client: TestClient) -> None:
    client.post("/api/requests", json={"problem": "First problem", "category": "other", "priority": "normal"})
    client.post("/api/requests", json={"problem": "Second problem", "category": "other", "priority": "normal"})

    response = client.get("/api/requests")
    body = response.json()
    assert len(body) == 2
    assert body[0]["problem"] == "Second problem"
    assert body[1]["problem"] == "First problem"


def test_create_request_rejects_invalid_category(client: TestClient) -> None:
    payload = {"problem": "Something broke", "category": "gardening", "priority": "normal"}
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422


def test_create_request_rejects_invalid_priority(client: TestClient) -> None:
    payload = {"problem": "Something broke", "category": "other", "priority": "critical"}
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422


def test_create_request_rejects_blank_problem(client: TestClient) -> None:
    payload = {"problem": "   ", "category": "other", "priority": "normal"}
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422


def test_create_request_rejects_missing_fields(client: TestClient) -> None:
    response = client.post("/api/requests", json={"problem": "Missing category and priority"})
    assert response.status_code == 422
