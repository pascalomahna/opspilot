from sqlalchemy import select
from sqlalchemy.orm import Session

from opspilot.db_models import ApplicationDB
from opspilot.models import ApplicationCreate


def list_applications(db: Session) -> list[ApplicationDB]:
    return list(db.scalars(select(ApplicationDB)).all())


def create_application(
    application: ApplicationCreate,
    db: Session,
) -> ApplicationDB:
    db_application = ApplicationDB(
        name=application.name,
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


def get_application(
    application_id: int,
    db: Session,
) -> ApplicationDB | None:
    return db.get(ApplicationDB, application_id)
