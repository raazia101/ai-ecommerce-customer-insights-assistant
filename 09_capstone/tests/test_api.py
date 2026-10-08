from fastapi.testclient import TestClient

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPSTONE_DIR = PROJECT_ROOT / "09_capstone"

if str(CAPSTONE_DIR) not in sys.path:
    sys.path.insert(0, str(CAPSTONE_DIR))

from api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_order_status():
    response = client.post(
        "/chat",
        json={
            "session_id": "pytest-order-session",
            "message": "What is the status of ORD-00001?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "pytest-order-session"
    assert data["trace_id"]
    assert data["response"] == "Order ORD-00001 has status pending."
    assert data["tool_used"] == "order_status"
    assert data["status"] == "success"


def test_chat_clarification():
    response = client.post(
        "/chat",
        json={
            "session_id": "pytest-clarification-session",
            "message": "What is the status?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "clarification"
    assert "order ID" in data["response"]


def test_chat_destructive_request_rejected():
    response = client.post(
        "/chat",
        json={
            "session_id": "pytest-safety-session",
            "message": "Cancel my order ORD-00001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "unsupported"
    assert data["tool_used"] is None
    assert "cannot perform destructive actions" in data["response"]


def test_chat_multi_turn_order_context():
    session_id = "pytest-multiturn-session"

    first_response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "What is the status of ORD-00001?",
        },
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "success"

    second_response = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "And what about that order?",
        },
    )

    assert second_response.status_code == 200

    data = second_response.json()

    assert data["response"] == "Order ORD-00001 has status pending."
    assert data["tool_used"] == "order_status"
    assert data["status"] == "success"


def test_clear_chat():
    session_id = "pytest-clear-session"

    client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "What is the status of ORD-00001?",
        },
    )

    response = client.delete(f"/chat/{session_id}")

    assert response.status_code == 200
    assert response.json() == {
        "session_id": session_id,
        "status": "cleared",
    }


def test_chat_invalid_request():
    response = client.post(
        "/chat",
        json={
            "session_id": "",
            "message": "",
        },
    )

    assert response.status_code == 422
