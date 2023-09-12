from datetime import datetime

from pydantic import BaseModel

from .test_selection import TestSelection


# Shared properties
class TestRunConfigBase(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    name: str
    dut_name: str
    selected_tests: TestSelection = {}


# Properties additional fields on  creation
class TestRunConfigCreate(TestRunConfigBase):
    pass


# Properties to receive on update (Only name can be updated)
class TestRunConfigUpdate(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    name: str


# Properties shared by models stored in DB
class TestRunConfigInDBBase(TestRunConfigBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class TestRunConfig(TestRunConfigInDBBase):
    pass


# Additional Properties properties stored in DB
class TestRunConfigInDB(TestRunConfigInDBBase):
    created_at: datetime


# Schema used for Export test run config
class TestRunConfigToExport(TestRunConfigBase):
    created_at: datetime

    class Config:
        orm_mode = True
