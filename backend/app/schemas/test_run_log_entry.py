from typing import Optional

from pydantic import BaseModel


class TestRunLogEntry(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    level: str
    timestamp: float
    message: str
    test_suite_execution_index: Optional[int]
    test_case_execution_index: Optional[int]
    test_step_execution_index: Optional[int]
