from enum import IntEnum

MESSAGE_EVENT_KEY = "message_event"
RESPONSE_KEY = "response"
STATUS_CODE_KEY = "status_code"


class UserResponseStatusEnum(IntEnum):
    OKAY = 0
    CANCELLED = -1
    TIMEOUT = -2
    INVALID = -3
