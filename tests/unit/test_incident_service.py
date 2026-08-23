from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from opspilot.db_models import IncidentDB
from opspilot.models import IncidentCreate, Severity
from opspilot.services.incidents import (
    create_incident,
    get_incident,
    list_incidents,
)


def test_create_incident_persists_incident() -> None:
    db = MagicMock(spec=Session)

    incident = IncidentCreate(
        title="Database unavailable",
        description="PostgreSQL cannot be reached.",
        severity=Severity.CRITICAL,
    )

    result = create_incident(incident, db)

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

    assert result.title == incident.title
    assert result.description == incident.description
    assert result.severity == Severity.CRITICAL.value


def test_get_incident_returns_incident() -> None:
    db = MagicMock(spec=Session)
    expected = IncidentDB(
        title="API unavailable",
        description="The API is not responding.",
        severity=Severity.HIGH.value,
    )

    db.get.return_value = expected

    result = get_incident(42, db)

    db.get.assert_called_once_with(IncidentDB, 42)
    assert result is expected


def test_get_incident_returns_none_when_not_found() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    result = get_incident(999, db)

    db.get.assert_called_once_with(IncidentDB, 999)
    assert result is None


def test_list_incidents_returns_all_incidents() -> None:
    db = MagicMock(spec=Session)

    incidents = [
        IncidentDB(
            title="Database unavailable",
            description="Database cannot be reached.",
            severity=Severity.CRITICAL.value,
        ),
        IncidentDB(
            title="Slow API",
            description="Response times are increased.",
            severity=Severity.MEDIUM.value,
        ),
    ]

    db.scalars.return_value.all.return_value = incidents

    result = list_incidents(db)

    db.scalars.assert_called_once()
    db.scalars.return_value.all.assert_called_once_with()

    assert result == incidents
