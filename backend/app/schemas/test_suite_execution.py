from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.test_enums import TestStateEnum

from .test_case_execution import TestCaseExecution, TestCaseExecutionToExport
from .test_suite_metadata import TestSuiteMetadata, TestSuiteMetadataBase


# Shared properties
class TestSuiteExecutionBase(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    state: TestStateEnum
    public_id: str
    execution_index: int


# Properties shared by models stored in DB
class TestSuiteExecutionInDBBase(TestSuiteExecutionBase):
    id: int
    test_run_execution_id: int
    test_suite_metadata_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    errors: Optional[List[str]]
    execution_index: int

    class Config:
        orm_mode = True


# Properties to return to client
class TestSuiteExecution(TestSuiteExecutionInDBBase):
    test_case_executions: List[TestCaseExecution]
    test_suite_metadata: TestSuiteMetadata


# Additional Properties properties stored in DB
class TestSuiteExecutionInDB(TestSuiteExecutionInDBBase):
    created_at: datetime


# Schema used for Export test suite executions
class TestSuiteExecutionToExport(TestSuiteExecutionBase):
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    errors: Optional[List[str]]
    test_case_executions: List[TestCaseExecutionToExport]
    test_suite_metadata: TestSuiteMetadataBase
    created_at: datetime

    class Config:
        orm_mode = True
