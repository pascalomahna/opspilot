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
    status: IncidentStatus | None = None
    application_id: int | None = None


class Incident(IncidentCreate):
    id: int
    status: IncidentStatus
    created_at: datetime
    application_id: int | None = None


class ApplicationCreate(BaseModel):
    name: str


class Application(ApplicationCreate):
    id: int
