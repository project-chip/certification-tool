from typing import Optional

from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.pics import PICS
from app.schemas.project import ProjectCreate
from app.tests.utils.utils import random_lower_string


def create_random_project(db: Session, pics: Optional[PICS] = PICS()) -> models.Project:
    name = random_lower_string()
    wifi_ssid = random_lower_string()
    project_in = ProjectCreate(name=name, wifi_ssid=wifi_ssid, pics=pics)
    return crud.project.create(db=db, obj_in=project_in)


def create_random_project_archived(db: Session) -> models.Project:
    project = create_random_project(db=db)
    return crud.project.archive(db=db, db_obj=project)
