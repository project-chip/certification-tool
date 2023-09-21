from unittest import mock

import pytest

from app.constants.websockets_constants import (
    MESSAGE_ID_KEY,
    MessageKeysEnum,
    MessageTypeEnum,
)
from app.user_prompt_support.user_prompt_manager import (
    PromptExchange,
    user_prompt_manager,
)


@pytest.mark.asyncio
async def test_send_prompt_request() -> None:
    """
    Validate the following during multiple calls to send_prompt_request():

    1. The list "active_prompts" contains a new PromptExchange object with every call.
    2. "messsage_id" of a new PromptExchange object increases with every call.
    """

    initial_message_id = user_prompt_manager.current_message_id

    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Mock async functions to return immediately
    with mock.patch.object(
        user_prompt_manager,
        "_UserPromptManager__send_message",
    ) as send_message, mock.patch.object(
        PromptExchange,
        "response",
    ) as response:
        iterations = 2

        for i in range(iterations):
            await user_prompt_manager.send_prompt_request(prompt=mock.MagicMock())
            assert user_prompt_manager.active_prompts is not None
            assert len(user_prompt_manager.active_prompts) == i + 1

            # Verify that the message ID has incremented
            assert (
                user_prompt_manager.active_prompts[i].message_id
                == initial_message_id + i + 1
            )

        # Verify that the prompt exchange objects are unique
        # by converting the list into a set to get unique prompts
        assert len(set(user_prompt_manager.active_prompts)) == iterations

        # Verify that the mocked functions are called
        assert send_message.call_count == iterations
        assert response.call_count == iterations

    # Cleanup
    user_prompt_manager.active_prompts.clear()


@pytest.mark.asyncio
async def test_received_message_with_empty_message_dict() -> None:
    """
    This tests received_message() by passing an empty message dictionary.

    Expected results:
    The pending prompts inside "active_prompts" list are intact.
    """
    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Populate "active_prompts"
    num_samples = 5
    for idx in range(num_samples):
        exchange = PromptExchange(prompt=mock.MagicMock(), message_id=idx)
        user_prompt_manager.active_prompts.append(exchange)

    user_prompt_manager.received_message(message_dict={}, socket=mock.MagicMock())

    # Validate that the "active prompt" entries are not lost
    assert len(user_prompt_manager.active_prompts) == num_samples
    for message_id, exchange in zip(
        range(num_samples), user_prompt_manager.active_prompts
    ):
        assert exchange.message_id == message_id

    # Cleanup
    user_prompt_manager.active_prompts.clear()


@pytest.mark.asyncio
async def test_received_message_with_invalid_message_id() -> None:
    """
    This tests the received_message() by passing a message dictionary with
    an invalid message_id.

    Expected results:
    The pending prompts inside "active_prompts" list are intact.
    """
    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Create sample "active_prompts"
    expected_active_prompts: list[PromptExchange] = []
    num_samples = 5
    for idx in range(num_samples):
        exchange = PromptExchange(prompt=mock.MagicMock(), message_id=idx)
        expected_active_prompts.append(exchange)

    # Populate "active_prompts", use copy to ensure 2 different lists
    user_prompt_manager.active_prompts = expected_active_prompts.copy()

    # Setup the message dictionary with an invalid message id
    invalid_message_id = -1
    test_message_dict = {MESSAGE_ID_KEY: invalid_message_id}

    user_prompt_manager.received_message(
        message_dict=test_message_dict, socket=mock.MagicMock()
    )
    # Validate that the "active prompt" entries are not lost
    assert len(user_prompt_manager.active_prompts) == num_samples
    assert user_prompt_manager.active_prompts == expected_active_prompts

    # Cleanup
    user_prompt_manager.active_prompts.clear()


@pytest.mark.asyncio
async def test_received_message_with_valid_message_id() -> None:
    """
    This tests the received_message() by passing a message dictionary with
    a valid message_id.

    Expected results:
    1. The pending prompts inside "active_prompts" list does not have
       the valid message_id.
    2. The matching prompt exchange object has the message_event set.
    3. The matching prompt exchange object's received response is not None.
    """
    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Populate "active_prompts"
    num_samples = 5
    for idx in range(num_samples):
        exchange = PromptExchange(prompt=mock.MagicMock(), message_id=idx)
        user_prompt_manager.active_prompts.append(exchange)

    # Setup the message dictionary with a valid message id
    test_message_id = 3
    test_message_dict = {MESSAGE_ID_KEY: test_message_id}

    # Record the matching prompt exchange object as it will be eventually
    # removed from "active_prompts"
    test_exchange = user_prompt_manager.active_prompts[test_message_id]

    # Message event is not set prior to calling received_message
    assert not test_exchange.message_event.is_set()

    user_prompt_manager.received_message(
        message_dict=test_message_dict, socket=mock.MagicMock()
    )

    # Validate that the "active_prompt" entries does not include "test_message_id"
    assert len(user_prompt_manager.active_prompts) == num_samples - 1
    for exchange in user_prompt_manager.active_prompts:
        assert exchange.message_id != test_message_id
        assert exchange != test_exchange

    # Validate that handle_response() is called
    assert test_exchange.message_event.is_set()
    assert test_exchange.received_response is not None

    # Cleanup
    user_prompt_manager.active_prompts.clear()


@pytest.mark.asyncio
async def test_prompt_timed_out_invalid_exchange() -> None:
    """
    This tests the prompt_timed_out() by passing an invalid prompt exchange object.

    Expected results:
    1. Ensure that an exception is raised.
    2. The pending prompts inside "active_prompts" list are intact.
    """
    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Populate "active_prompts"
    num_samples = 5
    for idx in range(num_samples):
        exchange = PromptExchange(prompt=mock.MagicMock(), message_id=idx)
        user_prompt_manager.active_prompts.append(exchange)

    # Setup the invalid prompt exchange
    invalid_prompt_exchange = PromptExchange(prompt=mock.MagicMock(), message_id=-1)

    with mock.patch.object(
        user_prompt_manager,
        "_UserPromptManager__send_message",
    ) as send_message, mock.patch.object(
        user_prompt_manager,
        "_UserPromptManager__timeout_broadcast_message",
    ) as timeout_broadcast_message:
        with pytest.raises(ValueError):
            await user_prompt_manager.prompt_timed_out(
                prompt_exchange=invalid_prompt_exchange
            )

            # Validate that the "active prompt" entries are not lost
            assert len(user_prompt_manager.active_prompts) == num_samples
            for message_id, exchange in zip(
                range(num_samples), user_prompt_manager.active_prompts
            ):
                assert exchange.message_id == message_id

            # Ensure that broadcast functions are not called
            assert send_message.call_count == 0
            assert timeout_broadcast_message.call_count == 0

    # Cleanup
    user_prompt_manager.active_prompts.clear()


@pytest.mark.asyncio
async def test_prompt_timed_out_valid_exchange() -> None:
    """
    This tests the prompt_timed_out() by passing a valid prompt exchange object.

    Expected results:
    1. The "active_prompts" list does not have the valid prompt exchange object.
    2. The timeout message is sent.
    """
    # Ensure that the "active_prompts" list is initially empty
    user_prompt_manager.active_prompts.clear()
    assert len(user_prompt_manager.active_prompts) == 0

    # Populate "active_prompts"
    num_samples = 5
    for idx in range(num_samples):
        exchange = PromptExchange(prompt=mock.MagicMock(), message_id=idx)
        user_prompt_manager.active_prompts.append(exchange)

    # Record the matching prompt exchange object as it will be eventually
    # removed from "active_prompts"
    test_message_id = 2
    test_exchange = user_prompt_manager.active_prompts[test_message_id]

    # Build the expected timeout message
    expected_message_dict = {
        MessageKeysEnum.TYPE: MessageTypeEnum.TIME_OUT_NOTIFICATION,
        MessageKeysEnum.PAYLOAD: {MESSAGE_ID_KEY: test_exchange.message_id},
    }

    with mock.patch.object(
        user_prompt_manager,
        "_UserPromptManager__send_message",
        side_effect=mock.AsyncMock,
    ) as send_message:
        await user_prompt_manager.prompt_timed_out(prompt_exchange=test_exchange)

        # Ensure that the timeout message is sent
        send_message.assert_called_once_with(expected_message_dict)

        # Validate that the "active_prompt" entries does not include "test_exchange"
        assert len(user_prompt_manager.active_prompts) == num_samples - 1
        for exchange in user_prompt_manager.active_prompts:
            assert exchange != test_exchange
            assert exchange.message_id != test_message_id

    # Cleanup
    user_prompt_manager.active_prompts.clear()
