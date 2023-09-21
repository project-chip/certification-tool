# this is needed (with import loguru) as types are not available at runtime
from __future__ import annotations

import asyncio
from asyncio import CancelledError, Task
from typing import Optional

import loguru  # this is needed (with __future__ annotations)
from loguru import logger

from app.schemas.test_run_log_entry import TestRunLogEntry
from app.test_engine.models import TestCase, TestRun, TestStep, TestSuite

LOG_PROCESSING_INTERVAL = 0.5


class TestLogHandler:
    """Responsible for attaching log messages to a Test Run.

    The log handler is registering a custom logger sink, that gets called for all log
    messages, logged via the test_engine_logger (these messages have `test_run_log` in
    the extra data). The log messages are annotated with current test_suite and
    test_case.

    We're putting the annotated messages on a queue, that is processed periodically.
    This is done to avoid the DB and UI being spammed with updates.
    """

    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    def __init__(self, test_run: TestRun) -> None:
        self.__test_run: TestRun = test_run
        self.__pending_log_entries: list[TestRunLogEntry] = []
        self.__logger_sink_id = self.__subscribe_to_test_run_log_messages()
        self.__process_entries_task: Task = asyncio.create_task(
            self.__periodically_process_entries()
        )
        self.__process_interval_in_sec = LOG_PROCESSING_INTERVAL

    @property
    def __current_test_suite(self) -> Optional[TestSuite]:
        return self.__test_run.current_test_suite

    @property
    def __current_test_case(self) -> Optional[TestCase]:
        if self.__current_test_suite is None:
            return None
        return self.__current_test_suite.current_test_case

    @property
    def __current_test_step(self) -> Optional[TestStep]:
        if (test_case := self.__current_test_case) is None:
            return None
        return test_case.current_test_step

    @property
    def __current_test_suite_index(self) -> Optional[int]:
        if (test_suite := self.__current_test_suite) is None:
            return None
        return test_suite.test_suite_execution.execution_index

    @property
    def __current_test_case_index(self) -> Optional[int]:
        if (test_case := self.__current_test_case) is None:
            return None
        return test_case.test_case_execution.execution_index

    @property
    def __current_test_step_index(self) -> Optional[int]:
        if (test_step := self.__current_test_step) is None:
            return None
        if (test_step_execution := test_step.test_step_execution) is None:
            return None
        return test_step_execution.execution_index

    async def finish(self) -> None:
        """Cancel the processing task and process remaining entries."""
        self.__unsubscribe_to_test_run_log_messages()

        self.__process_entries_task.cancel()
        await self.__process_entries_task

        await self.__process_pending_entries()

    def __subscribe_to_test_run_log_messages(self) -> int:
        """Add a logger sink for log messages, logged via the test_engine_logger.

        Returns:
            int: Id for logguru sink, can be used to remove sink from loguru.
        """
        return logger.add(
            self.__handle_test_run_log_message,
            filter=lambda record: "test_run_log" in record["extra"],
        )

    def __unsubscribe_to_test_run_log_messages(self) -> None:
        """Remove added logger sink."""
        logger.remove(self.__logger_sink_id)

    def __handle_test_run_log_message(self, message: loguru.Message) -> None:
        """Handles log messages, logged via test_engine_logger.

        Creates a test run log entry, associates all messages with current test suite
        and test case.

        The log entry is added to the queue of pending entries, to be handled by the
        scheduled proccessing task.

        Args:
            message (Message): log message from loguru
        """
        log_entry = TestRunLogEntry(
            level=message.record["level"].name,
            timestamp=message.record["time"].timestamp(),
            message=message.record["message"],
            test_suite_execution_index=self.__current_test_suite_index,
            test_case_execution_index=self.__current_test_case_index,
            test_step_execution_index=self.__current_test_step_index,
        )
        self.__pending_log_entries.append(log_entry)

    async def __periodically_process_entries(self) -> None:
        """This will process the pending entries at a pre-defined interval."""
        try:
            while True:
                await asyncio.gather(
                    self.__process_pending_entries(),
                    asyncio.sleep(self.__process_interval_in_sec),
                )
        except CancelledError:
            pass

    async def __process_pending_entries(self) -> None:
        if len(self.__pending_log_entries) == 0:
            return

        # test_run.append_log_entries will cause updating UI/DB so there's a risk
        # that new log entries are added during this call,
        # causing entries to be missed. Thus, using a copy and resetting pending.
        # This is an issue as loguru runs `__handle_test_run_log_message` on
        # a different thread.
        entries = self.__pending_log_entries
        self.__pending_log_entries = []

        self.__test_run.append_log_entries(entries)
