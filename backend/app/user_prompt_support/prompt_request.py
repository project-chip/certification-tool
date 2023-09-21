from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel

default_timeout_s = 60  # Seconds


class PromptRequestType(str, Enum):
    BASE = "base"
    OPTIONS = "options"
    TEXT = "text"
    FILE = "file"


class PromptRequest(BaseModel):
    prompt: Optional[str]
    timeout: int = default_timeout_s
    __type: PromptRequestType = PromptRequestType.BASE

    @property
    def type(self) -> PromptRequestType:
        return self.__type


class OptionsSelectPromptRequest(PromptRequest):
    __type = PromptRequestType.OPTIONS
    options: Dict[str, int]


class TextInputPromptRequest(PromptRequest):
    __type = PromptRequestType.TEXT
    placeholder_text: Optional[str]
    default_value: Optional[str]
    regex_pattern: Optional[str]


class UploadFilePromptRequest(PromptRequest):
    __type = PromptRequestType.FILE
    path: str = "api/v1/test_run_execution/file_upload/"
