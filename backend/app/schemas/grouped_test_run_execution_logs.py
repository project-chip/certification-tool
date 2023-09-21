from typing import Dict, List

from pydantic import BaseModel

from app.models.test_enums import TestStateEnum
from app.schemas.test_run_log_entry import TestRunLogEntry


class GroupedTestRunExecutionLogs(BaseModel):
    general: List[TestRunLogEntry] = []
    # test suite logs are indexed by the suite's public_id
    suites: Dict[str, List[TestRunLogEntry]] = {}
    # test case logs are grouped by state and then indexed by the test case's pubic_id
    cases: Dict[TestStateEnum, Dict[str, List[TestRunLogEntry]]] = {}
