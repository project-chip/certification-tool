from enum import Enum


class TestStateEnum(str, Enum):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    PENDING = "pending"
    EXECUTING = "executing"
    PENDING_ACTUATION = "pending_actuation"  # TODO: Do we need this
    PASSED = "passed"  # Test Passed with no issued
    FAILED = "failed"  # Test Failed
    ERROR = "error"  # Test Error due to tool setup or environment
    NOT_APPLICABLE = "not_applicable"  # TODO: Do we need this for full cert runs?
    CANCELLED = "cancelled"
