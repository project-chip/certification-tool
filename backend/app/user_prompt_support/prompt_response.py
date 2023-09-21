from typing import Optional, Union

from pydantic import BaseModel

from .constants import UserResponseStatusEnum


class PromptResponse(BaseModel):
    response: Union[Optional[int], Optional[str]]
    status_code: UserResponseStatusEnum
