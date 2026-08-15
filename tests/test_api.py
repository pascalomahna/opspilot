from fastapi.testclient import TestClient

from opspilot.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_incident() -> None:
    response = client.post(
        "/incidents",
        json={
            "title": "Checkout API unavailable",
            "description": "Customers receive HTTP 500 errors",
            "severity": "HIGH",
        },
    )
    
    assert response.status_code == 201
    
    body = response.json()
    
    assert body["title"] == "Checkout API unavailable"
    assert body["description"] == "Customers receive HTTP 500 errors"
    assert body["severity"] == "HIGH"
    assert body["status"] == "OPEN"
    assert body["id"] == 1