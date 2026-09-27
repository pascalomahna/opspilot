from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: Severity


class IncidentUpdate(BaseModel):
    status: IncidentStatus


class Incident(IncidentCreate):
    id: int
    status: IncidentStatus
    created_at: datetime
