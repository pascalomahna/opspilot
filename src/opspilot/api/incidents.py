from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from opspilot.database import get_db
from opspilot.db_models import IncidentDB
from opspilot.models import Incident, IncidentCreate, IncidentStatus, Severity
from opspilot.services import incidents as incident_service

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

DbSession = Annotated[Session, Depends(get_db)]


def to_incident(db_incident: IncidentDB) -> Incident:
    return Incident(
        id=db_incident.id,
        title=db_incident.title,
        description=db_incident.description,
        severity=Severity(db_incident.severity),
        status=IncidentStatus(db_incident.status),
        created_at=db_incident.created_at,
    )


@router.get("", response_model=list[Incident])
def list_incidents(db: DbSession) -> list[Incident]:
    incidents = incident_service.list_incidents(db)
    return [to_incident(incident) for incident in incidents]


@router.post("", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident: IncidentCreate,
    db: DbSession,
) -> Incident:
    db_incident = incident_service.create_incident(incident, db)
    return to_incident(db_incident)


@router.get("/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int,
    db: DbSession,
) -> Incident:
    db_incident = incident_service.get_incident(incident_id, db)

    if db_incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return to_incident(db_incident)
