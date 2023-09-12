from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .pics import PICS
from .test_environment_config import TestEnvironmentConfig


# Shared properties
class ProjectBase(BaseModel):
    name: Optional[str]
    config: Optional[TestEnvironmentConfig]
    pics: Optional[PICS]


# Properties additional fields on  creation
class ProjectCreate(ProjectBase):
    # Required on new projects
    name: str
    pics: PICS = PICS()
    # Note config is optional, but CRUD will add default config if not set.


# Properties to receive on update (Name and config can be updated)
class ProjectUpdate(ProjectBase):
    pass

    class Config:
        orm_mode = True


# Properties shared by models stored in DB
class ProjectInDBBase(ProjectCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]

    class Config:
        orm_mode = True


# Properties to return to client
class Project(ProjectInDBBase):
    pass

    class Config:
        orm_mode = True


# Additional Properties properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass
