from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.test_enums import TestStateEnum


# Shared properties
class TestStepExecutionBase(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    state: TestStateEnum
    title: str
    execution_index: int


# Properties shared by models stored in DB
class TestStepExecutionInDBBase(TestStepExecutionBase):
    id: int
    test_case_execution_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    errors: Optional[List[str]]
    failures: Optional[List[str]]
    execution_index: int

    class Config:
        orm_mode = True


# Properties to return to client
class TestStepExecution(TestStepExecutionInDBBase):
    pass


# Additional Properties properties stored in DB
class TestStepExecutionInDB(TestStepExecutionInDBBase):
    created_at: datetime


# Schema used for Export test step executions
class TestStepExecutionToExport(TestStepExecutionBase):
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    errors: Optional[List[str]]
    failures: Optional[List[str]]
    created_at: datetime

    class Config:
        orm_mode = True
