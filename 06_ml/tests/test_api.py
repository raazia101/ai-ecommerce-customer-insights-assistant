import sys
from pathlib import Path

from fastapi.testclient import TestClient


ML_DIR = Path(__file__).resolve().parents[1]

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from api.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready():
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_predict_validation():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={
                "customer_id": "TEST-001",
                "country": "UAE",
                "status": "active",
                "customer_tenure_days": -1,
                "completed_order_count": 2,
                "completed_revenue": 1000,
                "average_order_value": 500,
                "days_since_last_purchase": 30,
                "has_previous_purchase": 1,
                "total_transaction_count": 2,
                "failed_transaction_count": 0,
                "refunded_transaction_count": 0,
                "unique_products_purchased": 2,
                "unique_categories_purchased": 1,
                "total_event_count": 2,
                "product_view_count": 0,
                "add_to_cart_count": 0,
                "checkout_started_count": 0,
                "search_count": 0,
                "login_count": 1,
                "purchase_count": 1,
                "remove_from_cart_count": 0
            }
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_predict_success():
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={
                "customer_id": "TEST-001",
                "country": "UAE",
                "status": "active",
                "customer_tenure_days": 227,
                "completed_order_count": 2,
                "completed_revenue": 2746.51,
                "average_order_value": 1373.255,
                "days_since_last_purchase": 146,
                "has_previous_purchase": 1,
                "total_transaction_count": 4,
                "failed_transaction_count": 2,
                "refunded_transaction_count": 0,
                "unique_products_purchased": 7,
                "unique_categories_purchased": 3,
                "total_event_count": 6,
                "product_view_count": 0,
                "add_to_cart_count": 0,
                "checkout_started_count": 2,
                "search_count": 1,
                "login_count": 2,
                "purchase_count": 0,
                "remove_from_cart_count": 0,
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["customer_id"] == "TEST-001"
    assert body["prediction"] in [0, 1]
    assert 0 <= body["probability"] <= 1
    assert body["model_version"] == "week5-logistic-regression-v1"
    assert body["request_id"]
