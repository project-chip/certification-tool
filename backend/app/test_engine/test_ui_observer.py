from asyncio import Task, create_task, gather
from enum import Enum
from typing import Any, Optional, Union

from loguru import logger

from app.constants.websockets_constants import MessageKeysEnum, MessageTypeEnum
from app.models.test_enums import TestStateEnum
from app.schemas.test_run_log_entry import TestRunLogEntry
from app.socket_connection_manager import socket_connection_manager
from app.test_engine.models import TestCase, TestRun, TestStep, TestSuite
from app.test_engine.test_observer import Observer


class TestUpdateTypeEnum(str, Enum):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    TEST_RUN = "Test Run"
    TEST_SUITE = "Test Suite"
    TEST_STEP = "Test Step"
    TEST_CASE = "Test Case"


class TestUIObserver(Observer):
    __test__ = False
    __async_updates: list[Task] = []
    __last_seen_run_state: Optional[TestStateEnum] = None
    __last_seen_run_log_len = 0

    def dispatch(
        self, observable: Union[TestRun, TestSuite, TestCase, TestStep]
    ) -> None:
        logger.debug("Received Dispatch event")
        if observable is not None:
            if isinstance(observable, TestRun):
                self.__onTestRunUpdate(observable)
            if isinstance(observable, TestSuite):
                self.__onTestSuiteUpdate(observable)
            elif isinstance(observable, TestCase):
                self.__onTestCaseUpdate(observable)
            elif isinstance(observable, TestStep):
                self.__onTestStepUpdate(observable)

    def __onTestRunUpdate(self, observable: TestRun) -> None:
        logger.debug("Test Run Observer received", observable)
        self.__handle_test_run_state(observable)
        self.__handle_test_run_log(observable)

    def __handle_test_run_state(self, test_run: TestRun) -> None:
        """Send update to UI when test run state changes."""
        if self.__last_seen_run_state != test_run.state:
            message = {
                "test_type": TestUpdateTypeEnum.TEST_RUN,
                "body": {
                    "test_run_execution_id": test_run.test_run_execution.id,
                    "state": test_run.state,
                },
            }
            self.__send_test_update_message(message)
            self.__last_seen_run_state = test_run.state

    def __handle_test_run_log(self, test_run: TestRun) -> None:
        """Send update to UI with the latest log lines."""
        log_len = len(test_run.log)
        if log_len > self.__last_seen_run_log_len:
            new_entries = test_run.log[self.__last_seen_run_log_len :]
            self.__send_log_records_message(new_entries)
            self.__last_seen_run_log_len = log_len

    def __onTestSuiteUpdate(self, observable: TestSuite) -> None:
        logger.debug("Test Suite Observer received", observable)
        if observable.test_suite_execution is not None:
            test_suite_execution = observable.test_suite_execution
            update = {
                "test_suite_execution_index": test_suite_execution.execution_index,
                "state": observable.state,
                "errors": observable.errors,
            }
            self.__send_test_update_message(
                {"test_type": TestUpdateTypeEnum.TEST_SUITE, "body": update}
            )

    def __onTestCaseUpdate(self, observable: TestCase) -> None:
        logger.debug("Test Case Observer received", observable)
        if observable.test_case_execution is not None:
            test_case_execution = observable.test_case_execution
            test_suite_execution = test_case_execution.test_suite_execution
            update = {
                "test_suite_execution_index": test_suite_execution.execution_index,
                "test_case_execution_index": test_case_execution.execution_index,
                "state": observable.state,
                "errors": observable.errors,
            }
            self.__send_test_update_message(
                {"test_type": TestUpdateTypeEnum.TEST_CASE, "body": update}
            )

    def __onTestStepUpdate(self, observable: TestStep) -> None:
        if observable.test_step_execution is not None:
            test_step_execution = observable.test_step_execution
            test_case_execution = test_step_execution.test_case_execution
            test_suite_execution = test_case_execution.test_suite_execution
            update = {
                "test_suite_execution_index": test_suite_execution.execution_index,
                "test_case_execution_index": test_case_execution.execution_index,
                "test_step_execution_index": test_step_execution.execution_index,
                "state": observable.state,
                "errors": observable.errors,
                "failures": observable.failures,
            }
            self.__send_test_update_message(
                {"test_type": TestUpdateTypeEnum.TEST_STEP, "body": update}
            )

    def __send_test_update_message(self, update_payload: dict) -> None:
        self.__send_message(
            {
                MessageKeysEnum.TYPE: MessageTypeEnum.TEST_UPDATE,
                MessageKeysEnum.PAYLOAD: update_payload,
            }
        )

    def __send_log_records_message(self, log_entries: list[TestRunLogEntry]) -> None:
        self.__send_message(
            {
                MessageKeysEnum.TYPE: MessageTypeEnum.TEST_LOG_RECORDS,
                MessageKeysEnum.PAYLOAD: log_entries,
            }
        )

    def __send_message(self, message: dict[str, Any]) -> None:
        # enqueue update
        task = create_task(socket_connection_manager.broadcast(message))
        self.__async_updates.append(task)

    async def complete_tasks(self) -> None:
        pending_updates = self.__async_updates
        self.__async_updates = []
        await gather(*pending_updates)
