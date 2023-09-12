from asyncio import sleep

import pytest
from sqlalchemy.orm import Session

from app.models import TestRunExecution
from app.test_engine.logger import test_engine_logger
from app.test_engine.models import TestRun
from app.test_engine.test_log_handler import LOG_PROCESSING_INTERVAL, TestLogHandler
from app.tests.test_engine.test_runner import load_and_run_tool_unit_tests
from test_collections.tool_unit_tests.test_suite_expected import TestSuiteExpected
from test_collections.tool_unit_tests.test_suite_expected.tctr_expected_pass import (
    TCTRExpectedPass,
)


@pytest.mark.asyncio
async def test_test_log_handler_normal_flow() -> None:
    run = TestRun(test_run_execution=TestRunExecution())
    log_handler = TestLogHandler(run)

    # Assert initial queue is empty
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 0

    # Assert messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 1")
    test_engine_logger.info("log message 2")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 0

    # Assert messages are processed after log processing interval
    await sleep(LOG_PROCESSING_INTERVAL)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 2

    # Assert new messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 3")
    test_engine_logger.info("log message 4")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 2

    # Assert new messages are processed after log processing interval
    await sleep(LOG_PROCESSING_INTERVAL)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 4

    # Assert final messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 5")
    test_engine_logger.info("log message 6")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 4

    # Assert remaining messages are processed during finish()
    await log_handler.finish()
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 6


@pytest.mark.asyncio
async def test_test_log_handler_no_reuse() -> None:
    run = TestRun(test_run_execution=TestRunExecution())
    log_handler = TestLogHandler(run)

    # Assert initial queue is empty
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 0

    # Assert messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 1")
    test_engine_logger.info("log message 2")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 0

    # Assert messages are processed after log processing interval
    await sleep(LOG_PROCESSING_INTERVAL)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 2

    # Assert new messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 3")
    test_engine_logger.info("log message 4")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 2

    # Assert remaining messages are processed during finish()
    await log_handler.finish()
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 4

    # New run and handler
    run = TestRun(test_run_execution=TestRunExecution())
    log_handler = TestLogHandler(run)

    # Assert initial queue is empty
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 0

    # Assert messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 1")
    test_engine_logger.info("log message 2")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 0

    # Assert messages are processed after log processing interval
    await sleep(LOG_PROCESSING_INTERVAL)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 2

    # Assert new messages get added to queue, but are not processed yet
    test_engine_logger.info("log message 3")
    test_engine_logger.info("log message 4")
    assert len(log_handler._TestLogHandler__pending_log_entries) == 2  # type: ignore
    assert len(run.log) == 2

    # Assert remaining messages are processed during finish()
    await log_handler.finish()
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    assert len(run.log) == 4


@pytest.mark.asyncio
async def test_test_log_handler_metadata_exists(db: Session) -> None:
    # load and run a sample test suite
    runner, run, suite, case = await load_and_run_tool_unit_tests(
        db, TestSuiteExpected, TCTRExpectedPass
    )
    log_handler = TestLogHandler(run)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore
    # assert if there is a test suite execution index in the logs
    assert any(
        log_entry.test_suite_execution_index is not None
        and log_entry.test_suite_execution_index >= 0
        for log_entry in run.log
    )
    # assert if there is a test case execution index in the logs
    assert any(
        log_entry.test_case_execution_index is not None
        and log_entry.test_case_execution_index >= 0
        for log_entry in run.log
    )
    # assert if there is a test step execution index in the logs
    assert any(
        log_entry.test_step_execution_index is not None
        and log_entry.test_step_execution_index >= 0
        for log_entry in run.log
    )


@pytest.mark.asyncio
async def test_test_log_handler_metadata_value(db: Session) -> None:
    # load and run a sample test suite
    runner, run, suite, case = await load_and_run_tool_unit_tests(
        db, TestSuiteExpected, TCTRExpectedPass
    )
    log_handler = TestLogHandler(run)
    assert len(log_handler._TestLogHandler__pending_log_entries) == 0  # type: ignore

    # Expected test suite and test case execution id's from the test run.
    expected_test_suite_execution_index = run.test_suites[
        0
    ].test_suite_execution.execution_index
    expected_test_case_execution_index = (
        run.test_suites[0].test_cases[0].test_case_execution.execution_index
    )

    # TCTRExpectedPass test case has 3 test steps.
    # Expected test step 2 execution id from test run.
    # test_steps[1] corresponds to test step 2 in TCTRExpectedPass test case.

    assert (
        run.test_suites[0].test_cases[0].test_steps[1].test_step_execution is not None
    )
    expected_test_step_execution_index = (
        run.test_suites[0]
        .test_cases[0]
        .test_steps[1]
        .test_step_execution.execution_index
    )

    # Capture execution id of Test step 2 from log entry.
    # Test step 2 in TCTRExpectedPass test case logs "Executing Test Step: Test Step 2"
    actualLogEntry = next(
        (log for log in run.log if log.message == "Executing Test Step: Test Step 2")
    )

    # verify all execution ID's match as expected from the test run v/s log entry.
    assert (
        expected_test_suite_execution_index == actualLogEntry.test_suite_execution_index
    )
    assert (
        expected_test_case_execution_index == actualLogEntry.test_case_execution_index
    )
    assert (
        expected_test_step_execution_index == actualLogEntry.test_step_execution_index
    )
