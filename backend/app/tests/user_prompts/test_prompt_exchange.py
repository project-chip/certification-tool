from typing import Optional
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.user_prompt_support import user_prompt_manager
from app.user_prompt_support.constants import UserResponseStatusEnum
from app.user_prompt_support.prompt_request import PromptRequest
from app.user_prompt_support.prompt_response import PromptResponse
from app.user_prompt_support.user_prompt_manager import PromptExchange


def test_prompt_exchange_handle_empty_response() -> None:
    """
    This tests the handle_response() by passing an empty message dictionary.

    Expected results:
    1. No response is received
    2. Status code is INVALID
    3. Message event is set
    """
    exchange: PromptExchange = PromptExchange(prompt=MagicMock(), message_id=0)

    # Message event is not set prior to handling the response.
    assert not exchange.message_event.is_set()

    exchange.handle_response(message_dict={})

    assert exchange.received_response is not None
    assert exchange.received_response.status_code == UserResponseStatusEnum.INVALID
    assert exchange.message_event.is_set()


def test_prompt_exchange_handle_valid_status_response() -> None:
    """
    This tests the handle_response() by passing a message dictionary
    containing only the status code.

    Expected results:
    1. A response is received
    2. Status code in the response matches the code in the message dictionary
    3. Message event is set.
    """
    exchange: PromptExchange = PromptExchange(prompt=MagicMock(), message_id=0)
    expected_status_code = UserResponseStatusEnum.OKAY

    # Message event is not set prior to handling the response.
    assert not exchange.message_event.is_set()

    exchange.handle_response(message_dict={"status_code": expected_status_code.value})

    assert exchange.received_response is not None
    assert exchange.received_response.status_code == expected_status_code
    assert exchange.message_event.is_set()


def test_prompt_exchange_handle_valid_response() -> None:
    """
    This tests the handle_response() by passing both the status code and the
    response in the message dictionary.

    Expected results:
    1. A response is received
    2. Status code in the response matches the code in the message dictionary
    3. Contents of the response matches the one in the message dictionary
    4. Message event is set.
    """
    exchange: PromptExchange = PromptExchange(prompt=MagicMock(), message_id=0)
    expected_status_code = UserResponseStatusEnum.OKAY
    expected_response = "Test response"

    # Message event is not set prior to handling the response.
    assert not exchange.message_event.is_set()

    exchange.handle_response(
        message_dict={
            "response": expected_response,
            "status_code": expected_status_code.value,
        }
    )
    assert exchange.received_response is not None
    assert exchange.received_response.status_code == expected_status_code
    assert exchange.received_response.response == expected_response
    assert exchange.message_event.is_set()


@pytest.mark.asyncio
async def test_prompt_exchange_response_timeout() -> None:
    """
    This tests the timeout handling inside response()

    Expected results:
    1. A response is not received
    2. Status code in the response is set to TIMEOUT
    """
    # Set timeout to 0 to force wait_for() to raise an exception
    request: PromptRequest = PromptRequest(prompt="Test string", timeout=0)
    exchange: PromptExchange = PromptExchange(prompt=request, message_id=0)

    # Force prompt_timed_out() to not notify about the exception
    with mock.patch.object(
        user_prompt_manager.user_prompt_manager,
        "prompt_timed_out",
    ) as prompt_timed_out:
        await exchange.response()
        prompt_timed_out.assert_called_once()
        assert exchange.received_response is not None
        assert exchange.received_response.response is None
        assert exchange.received_response.status_code == UserResponseStatusEnum.TIMEOUT


@pytest.mark.asyncio
async def test_prompt_exchange_response_return_value() -> None:
    """
    This tests the return value of response() after explicitly setting the
    PromptExchange instance fields.

    Expected results:
    1. A response is received
    2. Contents of the response matches the expected response
    3. Status code in the response is matches the expected status code
    """
    exchange: PromptExchange = PromptExchange(prompt=PromptRequest(), message_id=0)
    expected_response = "Test Response"
    expected_status_code = UserResponseStatusEnum.OKAY

    # Set up Prompt response
    exchange.received_response = PromptResponse(
        response=expected_response, status_code=expected_status_code
    )

    # Manually set the message event, as setting the received_response directly
    # doesn't handle that.
    exchange.message_event.set()

    response: Optional[PromptResponse] = await exchange.response()
    assert response is not None
    assert response.status_code == expected_status_code
    assert response.response == expected_response
