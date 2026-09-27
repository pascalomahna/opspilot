from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from opspilot.database import get_db
from opspilot.db_models import ApplicationDB
from opspilot.models import Application, ApplicationCreate
from opspilot.services import applications as application_service

router = APIRouter(prefix="/applications", tags=["applications"])

DbSession = Annotated[Session, Depends(get_db)]


def to_application(db_application: ApplicationDB) -> Application:
    return Application(
        id=db_application.id,
        name=db_application.name,
    )


@router.get("", response_model=list[Application])
def list_applications(db: DbSession) -> list[Application]:
    applications = application_service.list_applications(db)
    return [to_application(application) for application in applications]


@router.post("", response_model=Application, status_code=status.HTTP_201_CREATED)
def create_application(
    application: ApplicationCreate,
    db: DbSession,
) -> Application:
    db_application = application_service.create_application(application, db)
    return to_application(db_application)


@router.get("/{application_id}", response_model=Application)
def get_application(
    application_id: int,
    db: DbSession,
) -> Application:
    db_application = application_service.get_application(application_id, db)

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return to_application(db_application)
