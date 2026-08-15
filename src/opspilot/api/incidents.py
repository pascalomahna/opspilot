from fastapi import APIRouter, HTTPException

from opspilot.models import Incident, IncidentCreate, IncidentStatus


router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)

incidents: list[Incident] = []


@router.get("")
def get_incidents() -> list[Incident]:
    return incidents


@router.post("", status_code=201)
def create_incident(data: IncidentCreate) -> Incident:
    incident = Incident(
        id=len(incidents) + 1,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=IncidentStatus.OPEN
    )
    
    incidents.append(incident)
    return incident


@router.get("/{incident_id}")
def get_incident(incident_id: int) -> Incident:
    for incident in incidents:
        if incident.id == incident_id:
            return incident
        
    raise HTTPException(
        status_code=404,
        detail="Incident not found"
    )