from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from opspilot.db_models import ApplicationDB
from opspilot.models import ApplicationCreate
from opspilot.services.applications import (
    create_application,
    get_application,
    list_applications,
)


def test_create_application_persists_application() -> None:
    db = MagicMock(spec=Session)

    application = ApplicationCreate(
        name="Payments API",
    )

    result = create_application(application, db)

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

    assert result.name == application.name


def test_get_application_returns_application() -> None:
    db = MagicMock(spec=Session)

    expected = ApplicationDB(
        name="Payments API",
    )

    db.get.return_value = expected

    result = get_application(42, db)

    db.get.assert_called_once_with(ApplicationDB, 42)
    assert result is expected


def test_get_application_returns_none_when_not_found() -> None:
    db = MagicMock(spec=Session)
    db.get.return_value = None

    result = get_application(999, db)

    db.get.assert_called_once_with(ApplicationDB, 999)
    assert result is None


def test_list_applications_returns_all_applications() -> None:
    db = MagicMock(spec=Session)

    applications = [
        ApplicationDB(name="Payments API"),
        ApplicationDB(name="Customer Portal"),
    ]

    db.scalars.return_value.all.return_value = applications

    result = list_applications(db)

    db.scalars.assert_called_once()
    db.scalars.return_value.all.assert_called_once_with()

    assert result == applications
