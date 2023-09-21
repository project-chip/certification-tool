from unittest import mock

import pytest

from app.user_prompt_support import user_prompt_manager
from app.user_prompt_support.user_prompt_support import (
    UserPromptError,
    UserPromptSupport,
)


@pytest.mark.asyncio
async def test_send_prompt_request_no_response() -> None:
    """
    Validate that send_prompt_request() raises an exception upon no response.
    """
    prompt_support = UserPromptSupport()

    with mock.patch.object(
        user_prompt_manager.user_prompt_manager,
        "send_prompt_request",
        return_value=None,
    ) as send_prompt_request:
        with pytest.raises(UserPromptError):
            await prompt_support.send_prompt_request(prompt_request=mock.MagicMock())
            send_prompt_request.assert_called_once()
