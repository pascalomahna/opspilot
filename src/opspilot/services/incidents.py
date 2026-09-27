from sqlalchemy import select
from sqlalchemy.orm import Session

from opspilot.db_models import IncidentDB
from opspilot.models import IncidentCreate, IncidentUpdate


def list_incidents(db: Session) -> list[IncidentDB]:
    return list(db.scalars(select(IncidentDB)).all())


def create_incident(
    incident: IncidentCreate,
    db: Session,
) -> IncidentDB:
    db_incident = IncidentDB(
        title=incident.title,
        description=incident.description,
        severity=incident.severity.value,
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


def update_incident_status(
    incident_id: int,
    update: IncidentUpdate,
    db: Session,
) -> IncidentDB | None:
    incident = db.get(IncidentDB, incident_id)

    if incident is None:
        return None

    incident.status = update.status.value

    db.commit()
    db.refresh(incident)

    return incident


def get_incident(
    incident_id: int,
    db: Session,
) -> IncidentDB | None:
    return db.get(IncidentDB, incident_id)
