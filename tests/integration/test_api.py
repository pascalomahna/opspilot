from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from opspilot.database import Base, get_db
from opspilot.main import app


class PytestSettings(BaseSettings):
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
    )


test_settings = PytestSettings()  # type: ignore[call-arg]

test_engine = create_engine(test_settings.test_database_url)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session]:
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


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


def test_update_incident() -> None:
    create_response = client.post(
        "/incidents",
        json={
            "title": "Database unavailable",
            "description": "PostgreSQL cannot be reached.",
            "severity": "CRITICAL",
        },
    )

    incident_id = create_response.json()["id"]

    response = client.patch(
        f"/incidents/{incident_id}",
        json={
            "status": "IN_PROGRESS",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == incident_id
    assert body["status"] == "IN_PROGRESS"


def test_update_incident_returns_404_when_incident_does_not_exist() -> None:
    response = client.patch(
        "/incidents/999999",
        json={
            "status": "RESOLVED",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_update_incident_rejects_invalid_status() -> None:
    create_response = client.post(
        "/incidents",
        json={
            "title": "Database unavailable",
            "description": "PostgreSQL cannot be reached.",
            "severity": "HIGH",
        },
    )

    incident_id = create_response.json()["id"]

    response = client.patch(
        f"/incidents/{incident_id}",
        json={
            "status": "BROKEN",
        },
    )

    assert response.status_code == 422


def test_get_incident() -> None:
    create_response = client.post(
        "/incidents",
        json={
            "title": "Checkout API unavailable",
            "description": "Customers receive HTTP 500 errors",
            "severity": "HIGH",
        },
    )

    incident_id = create_response.json()["id"]

    response = client.get(f"/incidents/{incident_id}")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == incident_id
    assert body["title"] == "Checkout API unavailable"
    assert body["status"] == "OPEN"


def test_get_incident_not_found() -> None:
    response = client.get("/incidents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Incident not found"}


def test_list_incidents_filters_by_status_and_severity() -> None:
    first = client.post(
        "/incidents",
        json={
            "title": "Critical open incident",
            "description": "First incident",
            "severity": "CRITICAL",
        },
    ).json()

    client.post(
        "/incidents",
        json={
            "title": "High open incident",
            "description": "Second incident",
            "severity": "HIGH",
        },
    ).json()

    third = client.post(
        "/incidents",
        json={
            "title": "Critical resolved incident",
            "description": "Third incident",
            "severity": "CRITICAL",
        },
    ).json()

    client.patch(
        f"/incidents/{third['id']}",
        json={
            "status": "RESOLVED",
        },
    )

    response = client.get(
        "/incidents",
        params={
            "status": "OPEN",
            "severity": "CRITICAL",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == first["id"]


def test_list_incidents_filters_by_severity() -> None:
    client.post(
        "/incidents",
        json={
            "title": "Critical incident",
            "description": "Critical",
            "severity": "CRITICAL",
        },
    )

    client.post(
        "/incidents",
        json={
            "title": "Low incident",
            "description": "Low",
            "severity": "LOW",
        },
    )

    response = client.get(
        "/incidents",
        params={
            "severity": "CRITICAL",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["severity"] == "CRITICAL"


def test_list_incidents_rejects_invalid_filter_value() -> None:
    response = client.get(
        "/incidents",
        params={
            "status": "BROKEN",
        },
    )

    assert response.status_code == 422


def test_list_incidents_without_filters_returns_all_incidents() -> None:
    first = client.post(
        "/incidents",
        json={
            "title": "First incident",
            "description": "First description",
            "severity": "HIGH",
        },
    ).json()

    second = client.post(
        "/incidents",
        json={
            "title": "Second incident",
            "description": "Second description",
            "severity": "LOW",
        },
    ).json()

    response = client.get("/incidents")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {incident["id"] for incident in body} == {
        first["id"],
        second["id"],
    }


def test_create_application() -> None:
    response = client.post(
        "/applications",
        json={
            "name": "Payments API",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Payments API"
    assert "id" in body


def test_list_applications() -> None:
    first = client.post(
        "/applications",
        json={
            "name": "Payments API",
        },
    ).json()

    second = client.post(
        "/applications",
        json={
            "name": "Customer Portal",
        },
    ).json()

    response = client.get("/applications")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {application["id"] for application in body} == {
        first["id"],
        second["id"],
    }


def test_get_application() -> None:
    created = client.post(
        "/applications",
        json={
            "name": "Payments API",
        },
    ).json()

    response = client.get(
        f"/applications/{created['id']}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created["id"]
    assert body["name"] == "Payments API"


def test_get_application_returns_404_when_not_found() -> None:
    response = client.get("/applications/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_assign_application_to_incident() -> None:
    application = client.post(
        "/applications",
        json={
            "name": "Payments API",
        },
    ).json()

    incident = client.post(
        "/incidents",
        json={
            "title": "Payment failures",
            "description": "Payments are failing.",
            "severity": "CRITICAL",
        },
    ).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={
            "application_id": application["id"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == incident["id"]
    assert body["application_id"] == application["id"]


def test_assign_non_existing_application_returns_404() -> None:
    incident = client.post(
        "/incidents",
        json={
            "title": "Payment failures",
            "description": "Payments are failing.",
            "severity": "HIGH",
        },
    ).json()

    response = client.patch(
        f"/incidents/{incident['id']}",
        json={
            "application_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
