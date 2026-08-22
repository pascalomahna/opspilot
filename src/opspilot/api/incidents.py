from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from opspilot.database import get_db
from opspilot.db_models import IncidentDB
from opspilot.models import Incident, IncidentCreate, IncidentStatus

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get("")
def get_incidents(db: DbSession) -> list[Incident]:
    result = db.scalars(select(IncidentDB).order_by(IncidentDB.id))

    return [
        Incident(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            status=incident.status,
        )
        for incident in result
    ]


@router.post("", status_code=201)
def create_incident(
    data: IncidentCreate,
    db: DbSession,
) -> Incident:
    incident = IncidentDB(
        title=data.title,
        description=data.description,
        severity=data.severity.value,
        status=IncidentStatus.OPEN.value,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return Incident(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
    )


@router.get("/{incident_id}")
def get_incident(
    incident_id: int,
    db: DbSession,
) -> Incident:
    incident = db.get(IncidentDB, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return Incident(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
    )
