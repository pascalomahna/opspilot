from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from opspilot.db_models import ApplicationDB, IncidentDB
from opspilot.exceptions import ApplicationNotFoundError
from opspilot.models import IncidentCreate, IncidentStatus, IncidentUpdate, Severity
from opspilot.services.incidents import (
    create_incident,
    get_incident,
    list_incidents,
    update_incident,
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


def test_update_incident_persists_change() -> None:
    db = MagicMock(spec=Session)

    incident = IncidentDB(
        title="API unavailable",
        description="The API is not responding.",
        severity=Severity.HIGH.value,
        status=IncidentStatus.OPEN.value,
    )

    db.get.return_value = incident

    update = IncidentUpdate(
        status=IncidentStatus.IN_PROGRESS,
    )

    result = update_incident(42, update, db)

    db.get.assert_called_once_with(IncidentDB, 42)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(incident)

    assert result is incident
    assert incident.status == IncidentStatus.IN_PROGRESS.value


def test_update_incident_returns_none_when_not_found() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    update = IncidentUpdate(status=IncidentStatus.RESOLVED)

    result = update_incident(999, update, db)

    db.get.assert_called_once_with(IncidentDB, 999)
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

    assert result is None


def test_update_incident_assigns_application() -> None:
    db = MagicMock(spec=Session)

    incident = IncidentDB(
        title="API unavailable",
        description="The API is not responding.",
        severity=Severity.HIGH.value,
        status=IncidentStatus.OPEN.value,
    )

    application = ApplicationDB(
        name="Payments API",
    )
    application.id = 7

    db.get.side_effect = [incident, application]

    update = IncidentUpdate(
        application_id=7,
    )

    result = update_incident(42, update, db)

    assert result is incident
    assert incident.application_id == 7

    assert db.get.call_count == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(incident)


def test_update_incident_raises_when_application_does_not_exist() -> None:
    db = MagicMock(spec=Session)

    incident = IncidentDB(
        title="API unavailable",
        description="The API is not responding.",
        severity=Severity.HIGH.value,
        status=IncidentStatus.OPEN.value,
    )

    db.get.side_effect = [incident, None]

    update = IncidentUpdate(
        application_id=999,
    )

    with pytest.raises(ApplicationNotFoundError):
        update_incident(42, update, db)

    db.commit.assert_not_called()


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


def test_list_incidents_applies_status_and_severity_filters() -> None:
    db = MagicMock(spec=Session)
    db.scalars.return_value.all.return_value = []

    result = list_incidents(
        db,
        status=IncidentStatus.OPEN,
        severity=Severity.CRITICAL,
    )

    assert result == []
    db.scalars.assert_called_once()

    query = db.scalars.call_args.args[0]

    sql = str(
        query.compile(
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "incidents.status = 'OPEN'" in sql
    assert "incidents.severity = 'CRITICAL'" in sql
