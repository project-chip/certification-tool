from enum import Enum

MESSAGE_ID_KEY = "message_id"

INVALID_JSON_ERROR_STR = "The message received is not a valid JSON object"
MISSING_TYPE_ERROR_STR = "The message is missing a type key"
NO_HANDLER_FOR_MSG_ERROR_STR = "There is no handler registered for this message type"


# Enum Keys for different types of messages currently supported by the tool
class MessageTypeEnum(str, Enum):
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    TEST_UPDATE = "test_update"
    TIME_OUT_NOTIFICATION = "time_out_notification"
    TEST_LOG_RECORDS = "test_log_records"
    INVALID_MESSAGE = "invalid_message"


# Enum keys used with messages at the top level
class MessageKeysEnum(str, Enum):
    TYPE = "type"
    PAYLOAD = "payload"
