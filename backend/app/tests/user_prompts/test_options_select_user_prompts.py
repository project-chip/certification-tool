from json import dumps
from typing import Any, Dict
from unittest import mock
from unittest.mock import DEFAULT, MagicMock, call

import pytest
from sqlalchemy.orm import Session

from app.constants.websockets_constants import (
    MESSAGE_ID_KEY,
    MessageKeysEnum,
    MessageTypeEnum,
)
from app.models.test_enums import TestStateEnum
from app.schemas.test_runner_status import TestRunnerState
from app.socket_connection_manager import socket_connection_manager
from app.tests.test_engine.test_runner import load_and_run_tool_unit_tests
from app.user_prompt_support.constants import (
    RESPONSE_KEY,
    STATUS_CODE_KEY,
    UserResponseStatusEnum,
)
from app.user_prompt_support.prompt_request import (
    OptionsSelectPromptRequest,
    PromptRequest,
)
from app.user_prompt_support.user_prompt_manager import (
    PromptExchange,
    user_prompt_manager,
)
from test_collections.tool_unit_tests.test_suite_async import TestSuiteAsync
from test_collections.tool_unit_tests.test_suite_async.tctr_user_prompt import (
    TCTROptionsSelectUserPrompt,
)

PROMPT_KEY = "prompt"
OPTIONS_KEY = "options"
TIMEOUT_KEY = "timeout"

# Test Variables
test_prompt = "Please select one of the following options"
test_options = {
    "Options 1": 1,
    "Options 2": 2,
    "Options 3": 3,
    "Options 4": 4,
}
test_timeout = 1


@pytest.mark.asyncio
async def test_options_select_user_prompts_basic(db: Session) -> None:
    __reset_current_message_id()

    # Stub the socket manager broadcast method
    with mock.patch.object(
        target=socket_connection_manager,
        attribute="broadcast",
        side_effect=broadcast_stub_response_okay,
    ) as broadcast:
        runner, run, suite, case = await load_and_run_tool_unit_tests(
            db, TestSuiteAsync, TCTROptionsSelectUserPrompt
        )

        # Assert broadcast was called with prompt_dict
        args_list = broadcast.call_args_list
        assert call(__expected_prompt_dict()) in args_list

        assert runner.state == TestRunnerState.IDLE
        assert run.state == TestStateEnum.PASSED
        assert suite.state == TestStateEnum.PASSED
        assert case.state == TestStateEnum.PASSED
        for step in case.test_steps:
            assert step.state == TestStateEnum.PASSED
    # Assert that active prompts list is 0
    assert len(user_prompt_manager.active_prompts) == 0


@pytest.mark.asyncio
async def test_two_options_select_user_prompts_that_timeout(db: Session) -> None:
    __reset_current_message_id()

    # Mock the socket manager broadcast method
    with mock.patch.object(
        target=socket_connection_manager, attribute="broadcast"
    ) as broadcast:
        runner, run, suite, case = await load_and_run_tool_unit_tests(
            db, TestSuiteAsync, TCTROptionsSelectUserPrompt, 2
        )

        # Assert broadcast was first called four with:
        # 1. prompt_dict no 1
        # 2. timeout_notification no 1
        # 3. prompt_dict no 2
        # 4. timeout_notification no 2
        expected_broadcast_calls = [
            call(__expected_prompt_dict(message_id=1)),
            call(__expected_timeout_notification_dict(message_id=1)),
            call(__expected_prompt_dict(message_id=2)),
            call(__expected_timeout_notification_dict(message_id=2)),
        ]
        args_list = broadcast.call_args_list
        assert all(item in args_list for item in expected_broadcast_calls)

        # Assert Test Case/Step states
        assert runner.state == TestRunnerState.IDLE
        assert suite.state == TestStateEnum.ERROR

        for test_case in suite.test_cases:
            assert test_case is not None
            assert test_case.state == TestStateEnum.ERROR
            # Assert test_steps
            # 1. pass
            # 2. error
            # 3. pending
            test_steps = test_case.test_steps
            assert len(test_steps) == 3
            assert test_steps[0].state == TestStateEnum.PASSED
            assert test_steps[1].state == TestStateEnum.ERROR
            assert test_steps[2].state == TestStateEnum.PENDING

        # Assert that active prompts list is 0
        assert len(user_prompt_manager.active_prompts) == 0


@pytest.mark.asyncio
async def test_options_select_user_prompts_timeout(db: Session) -> None:
    __reset_current_message_id()

    # Mock the socket manager broadcast method
    with mock.patch.object(
        target=socket_connection_manager, attribute="broadcast"
    ) as broadcast:
        runner, run, suite, case = await load_and_run_tool_unit_tests(
            db, TestSuiteAsync, TCTROptionsSelectUserPrompt
        )

        # Assert broadcast was first called twice with:
        # 1. prompt_dict
        # 2. timeout_notification
        expected_broadcast_calls = [
            call(__expected_prompt_dict()),
            call(__expected_timeout_notification_dict()),
        ]
        args_list = broadcast.call_args_list
        assert all(item in args_list for item in expected_broadcast_calls)

        assert runner.state == TestRunnerState.IDLE
        assert run.state == TestStateEnum.ERROR
        assert suite.state == TestStateEnum.ERROR
        assert case.state == TestStateEnum.ERROR
        # Assert test_steps
        # 1. pass
        # 2. error
        # 3. pending
        steps = case.test_steps
        assert len(steps) == 3
        assert steps[0].state == TestStateEnum.PASSED
        assert steps[1].state == TestStateEnum.ERROR
        assert steps[2].state == TestStateEnum.PENDING

    # Assert that active prompts list is 0
    assert len(user_prompt_manager.active_prompts) == 0


@pytest.mark.asyncio
async def test_options_select_user_prompt_manager_prompt(db: Session) -> None:
    __reset_current_message_id()

    # Mock broadcast
    with mock.patch.object(
        target=socket_connection_manager, attribute="broadcast"
    ) as broadcast:
        # Send user prompt
        prompt = __custom_options_select_prompt()
        response = await user_prompt_manager.send_prompt_request(prompt=prompt)

        # Assert broadcast was first called twice with:
        # 1. prompt_dict
        # 2. timeout_notification
        expected_broadcast_calls = [
            call(__expected_prompt_dict(timeout=prompt.timeout)),
            call(__expected_timeout_notification_dict()),
        ]
        args_list = broadcast.call_args_list
        assert all(item in args_list for item in expected_broadcast_calls)

        assert response is not None
        assert response.status_code == UserResponseStatusEnum.TIMEOUT


@pytest.mark.asyncio
async def test_options_select_user_prompt_manager_response(db: Session) -> None:
    # Create and add the prompt to the user prompt manager list
    prompt = __custom_options_select_prompt_exchange()

    user_prompt_manager.active_prompts.append(prompt)

    # Send response to the prompt manager
    socket = MagicMock()
    await socket_connection_manager.received_message(
        socket=socket, message=dumps(__expected_response_dict_okay())
    )

    # Verify the user response properties
    response = await prompt.response()
    assert response is not None
    assert response.status_code == UserResponseStatusEnum.OKAY
    assert response.response == 1

    prompt.message_id = 2
    user_prompt_manager.active_prompts.append(prompt)
    await socket_connection_manager.received_message(
        socket=socket, message=dumps(__expected_response_dict_cancelled())
    )

    # Verify the user response properties
    user_response = await prompt.response()
    assert user_response is not None
    assert user_response.status_code == UserResponseStatusEnum.CANCELLED
    assert user_response.response == 1


async def broadcast_stub_response_okay(*args: Any, **kwargs: Any) -> Any:
    # Call the received message with the expected response
    socket = MagicMock()
    await socket_connection_manager.received_message(
        socket=socket, message=dumps(__expected_response_dict_okay())
    )
    return DEFAULT


# Helper Methods
def __reset_current_message_id() -> None:
    # We use the secret accessor to set the private variable
    user_prompt_manager._UserPromptManager__current_message_id = 0  # type: ignore


def __custom_options_select_prompt() -> PromptRequest:
    return OptionsSelectPromptRequest(
        prompt=test_prompt, options=test_options, timeout=test_timeout
    )


def __custom_options_select_prompt_exchange() -> PromptExchange:
    prompt = OptionsSelectPromptRequest(
        prompt=test_prompt, options=test_options, timeout=test_timeout
    )
    print(prompt)
    return PromptExchange(prompt=prompt, message_id=1)


def __expected_response_dict_okay() -> Dict[MessageKeysEnum, Any]:
    return {
        MessageKeysEnum.TYPE: MessageTypeEnum.PROMPT_RESPONSE,
        MessageKeysEnum.PAYLOAD: {
            RESPONSE_KEY: 1,
            STATUS_CODE_KEY: UserResponseStatusEnum.OKAY,
            MESSAGE_ID_KEY: 1,
        },
    }


def __expected_timeout_notification_dict(
    message_id: int = 1,
) -> Dict[MessageKeysEnum, Any]:
    return {
        MessageKeysEnum.TYPE: MessageTypeEnum.TIME_OUT_NOTIFICATION,
        MessageKeysEnum.PAYLOAD: {MESSAGE_ID_KEY: message_id},
    }


def __expected_response_dict_cancelled() -> Dict[str, Any]:
    return {
        MessageKeysEnum.TYPE: MessageTypeEnum.PROMPT_RESPONSE,
        MessageKeysEnum.PAYLOAD: {
            RESPONSE_KEY: 1,
            STATUS_CODE_KEY: UserResponseStatusEnum.CANCELLED,
            MESSAGE_ID_KEY: 2,
        },
    }


def __expected_prompt_dict(timeout: int = 2, message_id: int = 1) -> Dict[str, Any]:
    return {
        MessageKeysEnum.TYPE: MessageTypeEnum.PROMPT_REQUEST,
        MessageKeysEnum.PAYLOAD: {
            OPTIONS_KEY: test_options,
            TIMEOUT_KEY: timeout,
            PROMPT_KEY: test_prompt,
            MESSAGE_ID_KEY: message_id,
        },
    }
