import asyncio

import pytest
from sqlalchemy.orm import Session

from app.models.test_enums import TestStateEnum
from app.schemas.test_run_log_entry import TestRunLogEntry
from app.test_engine.test_db_observer import TestDBObserver
from app.test_engine.test_script_manager import TestScriptManager
from app.tests.utils.test_run_execution import (
    create_test_run_execution_with_some_test_cases,
)


@pytest.mark.asyncio
async def test_test_db_observer_test_run_started_at(db: Session) -> None:
    test_script_manager = TestScriptManager()
    test_db_observer = TestDBObserver()

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Getting newly created test run
    test_run = test_script_manager.get_test_run(db, test_run_execution)

    # Changing Test run state to executing state
    test_run.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_run)
    assert TestStateEnum.EXECUTING == test_run_execution.state
    assert test_run_execution.started_at is not None
    assert test_run_execution.completed_at is None
    assert len(test_run.log) == 0

    # Note original start time
    start_time = test_run_execution.started_at

    # Wait/sleep and Dispatch again to trigger DB update
    log_entry = TestRunLogEntry(level="info", timestamp=0.0, message="Message1")
    test_run.append_log_entries([log_entry])
    await asyncio.sleep(2)

    test_db_observer.dispatch(test_run)
    assert TestStateEnum.EXECUTING == test_run_execution.state
    assert len(test_run_execution.log) == 1
    assert test_run_execution.started_at == start_time
    assert test_run_execution.completed_at is None
    assert len(test_run.log) == 1


@pytest.mark.asyncio
async def test_test_db_observer_test_suite_started_at(db: Session) -> None:
    test_script_manager = TestScriptManager()
    test_db_observer = TestDBObserver()

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Getting newly created test suites
    test_run = test_script_manager.get_test_run(db, test_run_execution)
    test_suites = test_run.test_suites
    assert 1 == len(test_suites)
    test_suite = test_suites[0]

    # Changing Test suite state to executing state
    test_suite.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_suite)
    assert TestStateEnum.EXECUTING == test_run_execution.test_suite_executions[0].state
    assert test_run_execution.test_suite_executions[0].started_at is not None
    assert test_run_execution.test_suite_executions[0].completed_at is None
    assert len(test_run_execution.log) == 0

    # Note original start time
    start_time = test_run_execution.test_suite_executions[0].started_at

    # Wait/sleep and Dispatch again to trigger DB update
    test_run_execution.append_to_log(
        TestRunLogEntry(message="Wait for 2 seconds", level="Debug", timestamp=0)
    )
    await asyncio.sleep(2)

    test_db_observer.dispatch(test_suite)
    assert TestStateEnum.EXECUTING == test_run_execution.test_suite_executions[0].state
    assert test_run_execution.test_suite_executions[0].started_at == start_time
    assert test_run_execution.test_suite_executions[0].completed_at is None
    assert len(test_run_execution.log) == 1


@pytest.mark.asyncio
async def test_test_db_observer_test_case_started_at(db: Session) -> None:
    test_script_manager = TestScriptManager()
    test_db_observer = TestDBObserver()

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Getting newly created test suites
    test_run = test_script_manager.get_test_run(db, test_run_execution)
    test_suites = test_run.test_suites
    assert 1 == len(test_suites)
    test_suite = test_suites[0]

    assert 6 == len(test_suite.test_cases)
    test_case = test_suite.test_cases[0]

    # Changing Test case state to executing state
    test_case.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_case)
    assert TestStateEnum.EXECUTING == test_case.test_case_execution.state
    assert test_case.test_case_execution.started_at is not None
    assert test_case.test_case_execution.completed_at is None

    # Note original start time
    start_time = test_case.test_case_execution.started_at

    # Wait/sleep and Dispatch again to trigger DB update
    await asyncio.sleep(2)

    test_db_observer.dispatch(test_case)
    assert TestStateEnum.EXECUTING == test_case.test_case_execution.state
    assert test_case.test_case_execution.started_at == start_time
    assert test_case.test_case_execution.completed_at is None


@pytest.mark.asyncio
async def test_test_db_observer_test_step_started_at(db: Session) -> None:
    test_script_manager = TestScriptManager()
    test_db_observer = TestDBObserver()

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Getting newly created test suites
    test_run = test_script_manager.get_test_run(db, test_run_execution)
    test_suites = test_run.test_suites
    assert 1 == len(test_suites)
    test_suite = test_suites[0]

    assert 6 == len(test_suite.test_cases)
    test_case = test_suite.test_cases[0]

    test_step = test_case.test_steps[0]

    # Changing Test case state to executing state
    test_step.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_step)
    assert TestStateEnum.EXECUTING == test_step.state
    assert test_step.test_step_execution is not None
    assert test_step.test_step_execution.started_at is not None
    assert test_step.test_step_execution.completed_at is None

    # Note original start time
    start_time = test_step.test_step_execution.started_at

    # Wait/sleep and Dispatch again to trigger DB update
    await asyncio.sleep(2)

    test_db_observer.dispatch(test_step)
    assert TestStateEnum.EXECUTING == test_step.state
    assert test_step.test_step_execution is not None
    assert test_step.test_step_execution.started_at == start_time
    assert test_step.test_step_execution.completed_at is None


def test_test_db_observer_update(db: Session) -> None:
    test_script_manager = TestScriptManager()
    test_db_observer = TestDBObserver()

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Getting newly created test suites
    test_run = test_script_manager.get_test_run(db, test_run_execution)
    test_suites = test_run.test_suites
    assert 1 == len(test_suites)
    test_suite = test_suites[0]

    # Changing Test suite state to executing state
    test_suite.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_suite)
    assert TestStateEnum.EXECUTING == test_run_execution.test_suite_executions[0].state
    assert test_run_execution.test_suite_executions[0].started_at is not None

    # Adding an error to a Test suite
    suite_error = "This is a test suite error"
    test_suite.record_error(suite_error)

    test_db_observer.dispatch(test_suite)
    assert test_suite.test_suite_execution.errors is not None
    assert suite_error in test_suite.test_suite_execution.errors

    # Changing Test suite state to passed state

    test_suite.state = TestStateEnum.PASSED

    test_db_observer.dispatch(test_suite)
    assert TestStateEnum.PASSED == test_run_execution.test_suite_executions[0].state
    assert test_run_execution.test_suite_executions[0].completed_at is not None

    # Fetching Test cases.
    assert 6 == len(test_suite.test_cases)
    test_case = test_suite.test_cases[0]

    # Changing Test case state to executing state

    test_case.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_case)
    assert TestStateEnum.EXECUTING == test_case.test_case_execution.state
    assert test_case.test_case_execution.started_at is not None

    # Adding an error to a Test case
    case_error = "This is a test case error"
    test_case.record_error(case_error)

    test_db_observer.dispatch(test_case)
    assert test_case.test_case_execution.errors is not None
    assert case_error in test_case.test_case_execution.errors

    # Changing Test case state to passed state

    test_case.state = TestStateEnum.PASSED

    test_db_observer.dispatch(test_case)
    assert TestStateEnum.PASSED == test_case.test_case_execution.state
    assert test_case.test_case_execution.completed_at is not None

    test_step = test_case.test_steps[0]

    # Changing Test step state to executing state

    test_step.state = TestStateEnum.EXECUTING

    test_db_observer.dispatch(test_step)
    assert test_step.test_step_execution is not None

    assert TestStateEnum.EXECUTING == test_step.test_step_execution.state
    assert test_step.test_step_execution.started_at is not None

    # Changing Test step state to passed state

    test_step.state = TestStateEnum.PASSED

    test_db_observer.dispatch(test_step)
    assert TestStateEnum.PASSED == test_step.test_step_execution.state
    assert test_step.test_step_execution.completed_at is not None

    # Adding an error to a Test step
    step_error = "This is a test step error"
    test_step.errors = [step_error]

    test_db_observer.dispatch(test_step)
    assert test_step.test_step_execution.errors is not None
    assert step_error in test_step.test_step_execution.errors

    # Adding a failure to a Test step
    step_failure = "This is a test step failure"
    test_step.failures = [step_failure]

    test_db_observer.dispatch(test_step)
    assert test_step.test_step_execution.failures is not None
    assert step_failure in test_step.test_step_execution.failures

    # Adding a test case with the DB session is closed, expecting new session to be
    # created and save operation to succeed.
    test_step.state = TestStateEnum.EXECUTING
    db.close()
    test_db_observer.dispatch(test_step)
    assert TestStateEnum.EXECUTING == test_step.test_step_execution.state
