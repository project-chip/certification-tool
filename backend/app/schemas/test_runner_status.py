from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TestRunnerState(Enum):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    RUNNING = "running"


# Shared properties
class TestRunnerStatus(BaseModel):
    state: TestRunnerState
    test_run_execution_id: Optional[int]
