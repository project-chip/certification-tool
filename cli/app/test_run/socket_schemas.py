from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

MESSAGE_EVENT_KEY = "message_event"
RESPONSE_KEY = "response"
STATUS_CODE_KEY = "status_code"


# Enum Keys for different types of messages currently supported by the tool
class MessageTypeEnum(str, Enum):
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    TEST_UPDATE = "test_update"
    TIME_OUT_NOTIFICATION = "time_out_notification"
    TEST_LOG_RECORDS = "test_log_records"
    INVALID_MESSAGE = "invalid_message"


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


class UserResponseStatusEnum(IntEnum):
    OKAY = 0
    CANCELLED = -1
    TIMEOUT = -2
    INVALID = -3


class TestUpdateBase(BaseModel):
    state: TestStateEnum
    errors: Optional[List[str]]
    failures: Optional[List[str]]


class TestRunUpdate(TestUpdateBase):
    test_run_execution_id: int


class TestSuiteUpdate(TestUpdateBase):
    test_suite_execution_id: int


class TestCaseUpdate(TestSuiteUpdate):
    test_case_execution_id: int


class TestStepUpdate(TestCaseUpdate):
    test_step_execution_id: int


class TestUpdate(BaseModel):
    test_type: str
    body: Union[TestStepUpdate, TestCaseUpdate, TestSuiteUpdate, TestRunUpdate]


class TimeOutNotification(BaseModel):
    message_id: int


class TestLogRecord(BaseModel):
    level: str
    timestamp: str
    message: str
    test_suite_execution_id: Optional[int]
    test_case_execution_id: Optional[int]


class PromptRequest(BaseModel):
    prompt: str
    timeout: int
    message_id: int


class OptionsSelectPromptRequest(PromptRequest):
    options: Dict[str, int]


class TextInputPromptRequest(PromptRequest):
    placeholder_text: Optional[str]
    default_value: Optional[str]
    regex_pattern: Optional[str]


class PromptResponse(BaseModel):
    response: Union[int, str]
    status_code: UserResponseStatusEnum
    message_id: int


class SocketMessage(BaseModel):
    type: MessageTypeEnum
    payload: Union[
        OptionsSelectPromptRequest,
        TextInputPromptRequest,
        PromptResponse,
        TestUpdate,
        TimeOutNotification,
        List[TestLogRecord],
    ]
