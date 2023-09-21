from typing import Tuple

import pytest
from sqlalchemy.orm import Session

from app.models.test_enums import TestStateEnum
from app.test_engine.models import TestCase, TestSuite
from app.tests.utils.test_runner import (
    get_test_case_for_public_id,
    get_test_suite_for_public_id,
    load_and_run_tool_unit_tests,
    load_test_run_for_test_cases,
)
from test_collections.tool_unit_tests.test_suite_exceptions import TestSuiteExceptions
from test_collections.tool_unit_tests.test_suite_exceptions.tc_exception import (
    TCException,
)


@pytest.mark.asyncio
async def test_exception_test_suite_setup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = True
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert error was caught and recorded
    assert test_suite.state is TestStateEnum.ERROR
    assert test_suite.errors is not None
    # Expect 1 error from setup
    assert len(test_suite.errors) == 1
    error_msg = test_suite.errors[0]
    assert "setup" in error_msg.lower()

    # assert test_case is cancelled
    assert test_case.state == TestStateEnum.CANCELLED

    # assert test_steps are cancelled
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_exception_test_suite_cleanup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = True

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert error was caught and recorded
    assert test_suite.state is TestStateEnum.ERROR
    assert test_suite.errors is not None

    # Expect 1 error from setup and cleanup
    assert len(test_suite.errors) == 1
    error_msg = test_suite.errors[0]
    assert "cleanup" in error_msg.lower()

    # assert test_case is passed
    assert test_case.state == TestStateEnum.PASSED

    # assert test_steps are passed
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PASSED


@pytest.mark.asyncio
async def test_exception_test_suite_setup_and_cleanup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = True
    TestSuiteExceptions.error_during_cleanup = True

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert error was caught and recorded
    assert test_suite.state is TestStateEnum.ERROR
    assert test_suite.errors is not None

    # Expect 2 error from setup and cleanup
    assert len(test_suite.errors) == 2

    # assert test_case is cancelled
    assert test_case.state == TestStateEnum.CANCELLED

    # assert test_steps are cancelled
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_exception_test_case_setup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = True
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors == []

    # Assert test_case error is recorded
    assert test_case.state == TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 1 error from setup
    assert len(test_case.errors) == 1
    error_msg = test_case.errors[0]
    assert "setup" in error_msg.lower()

    # assert test_steps are pending
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PENDING


@pytest.mark.asyncio
async def test_exception_test_case_execution(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = True
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors == []

    # Assert test_case state is error as a test step failed
    test_case.state = TestStateEnum.ERROR

    # Assert test_case has no errors it self
    assert test_case.errors == []

    # Test case expected to fail on 2nd step
    assert len(test_case.test_steps) == 3

    # Step 1
    assert test_case.test_steps[0].state == TestStateEnum.PASSED

    # Step 2
    step2 = test_case.test_steps[1]
    assert step2.state == TestStateEnum.ERROR
    assert step2.errors is not None
    assert len(step2.errors) == 1
    error_msg = step2.errors[0]
    assert "execution" in error_msg.lower()

    # Step 3
    assert test_case.test_steps[2].state == TestStateEnum.PENDING


@pytest.mark.asyncio
async def test_exception_test_case_cleanup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = True

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors == []

    # Assert test_case error is recorded
    assert test_case.state == TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 1 error from cleanup
    assert len(test_case.errors) == 1
    error_msg = test_case.errors[0]
    assert "cleanup" in error_msg.lower()

    # Assert test_steps are passed
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PASSED


@pytest.mark.asyncio
async def test_exception_test_case_setup_and_cleanup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = True
    TCException.error_during_execute = False
    TCException.error_during_cleanup = True

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors == []

    # Assert test_case error is recorded
    assert test_case.state == TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 2 error from setup and cleanup
    assert len(test_case.errors) == 2

    # assert test_steps are pending
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PENDING


@pytest.mark.asyncio
async def test_exception_test_case_execution_and_cleanup(db: Session) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = True
    TCException.error_during_cleanup = True

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors == []

    # Assert test_case error is recorded
    assert test_case.state == TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 1 error from cleanup
    assert len(test_case.errors) == 1
    error_msg = test_case.errors[0]
    assert "cleanup" in error_msg.lower()

    # Test case expected to fail on 2nd step
    assert len(test_case.test_steps) == 3

    # Step 1
    assert test_case.test_steps[0].state == TestStateEnum.PASSED

    # Step 2
    step2 = test_case.test_steps[1]
    assert step2.state == TestStateEnum.ERROR
    assert step2.errors is not None
    assert len(step2.errors) == 1
    error_msg = step2.errors[0]
    assert "execution" in error_msg.lower()

    # Step 3
    test_case.test_steps[2].state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_exception_test_case_setup_and_test_suite_cleanup(
    db: Session,
) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = True

    # Configure Test Case Errors
    TCException.error_during_setup = True
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors is not None
    assert len(test_suite.errors) == 1
    error_msg = test_suite.errors[0]
    assert "cleanup" in error_msg.lower()

    # Assert test_case error is recorded
    assert test_case.state == TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 2 error from execute
    assert len(test_case.errors) == 1
    error_msg = test_case.errors[0]
    assert "setup" in error_msg.lower()

    # assert test_steps are pending
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PENDING


@pytest.mark.asyncio
async def test_exception_test_case_execution_and_test_suite_cleanup(
    db: Session,
) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = True

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = True
    TCException.error_during_cleanup = False

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors is not None
    assert len(test_suite.errors) == 1
    error_msg = test_suite.errors[0]
    assert "cleanup" in error_msg.lower()

    # Assert test_case error is recorded as test step failed
    test_case.state = TestStateEnum.ERROR

    # Assert test_case has no errors it self
    assert test_case.errors == []

    # Test case expected to fail on 2nd step
    assert len(test_case.test_steps) == 3

    # Step 1
    assert test_case.test_steps[0].state == TestStateEnum.PASSED

    # Step 2
    step2 = test_case.test_steps[1]
    assert step2.state == TestStateEnum.ERROR
    assert step2.errors is not None
    assert len(step2.errors) == 1
    error_msg = step2.errors[0]
    assert "execution" in error_msg.lower()

    # Step 3
    test_case.test_steps[2].state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_exception_test_case_cleanup_and_test_suite_cleanup(
    db: Session,
) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = False
    TestSuiteExceptions.error_during_cleanup = True

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = True

    # Run tests, and get test_suite and test_case for assertions
    test_suite, test_case = await __run_exception_tests(db)

    # Assert test suite state is error as one test case failed
    assert test_suite.state is TestStateEnum.ERROR

    # Assert test_suite has no errors it self
    assert test_suite.errors is not None
    assert len(test_suite.errors) == 1
    error_msg = test_suite.errors[0]
    assert "cleanup" in error_msg.lower()

    # assert test_case error is recorded
    test_case.state = TestStateEnum.ERROR
    assert test_case.errors is not None

    # Expect 2 error from execute
    assert len(test_case.errors) == 1
    error_msg = test_case.errors[0]
    assert "cleanup" in error_msg.lower()

    # Assert test_steps are passed
    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PASSED


@pytest.mark.asyncio
async def test_exception_1st_test_suite_error_2nd_pass(
    db: Session,
) -> None:
    # Configure Test Suite Errors
    TestSuiteExceptions.error_during_setup = True
    TestSuiteExceptions.error_during_cleanup = False

    # Configure Test Case Errors
    TCException.error_during_setup = False
    TCException.error_during_execute = False
    TCException.error_during_cleanup = False

    # Run 2 test_suites, and get test_suite and test_case for assertions
    test_suite_id_1 = "TestSuiteExceptions"
    test_case_id_1 = "TCException"
    test_suite_id_2 = "TestSuiteExpected"
    test_case_id_2 = "TCTRExpectedPass"
    selected_tests = {
        "tool_unit_tests": {
            test_suite_id_1: {test_case_id_1: 1},
            test_suite_id_2: {test_case_id_2: 1},
        }
    }
    test_runner = load_test_run_for_test_cases(db=db, test_cases=selected_tests)
    # Save test_run reference to inspect models after completion
    test_run = test_runner.test_run
    assert test_run is not None

    await test_runner.run()

    # Get Test suites
    test_suite_1 = get_test_suite_for_public_id(
        test_run=test_run, public_id=test_suite_id_1
    )
    test_suite_2 = get_test_suite_for_public_id(
        test_run=test_run, public_id=test_suite_id_2
    )
    assert test_suite_1 is not None
    assert test_suite_2 is not None

    # Assert test suite state is error as one test case failed
    assert test_suite_1.state is TestStateEnum.ERROR
    assert test_suite_2.state is TestStateEnum.PASSED

    # Get test cases
    test_case_1 = get_test_case_for_public_id(
        test_suite=test_suite_1, public_id=test_case_id_1
    )
    test_case_2 = get_test_case_for_public_id(
        test_suite=test_suite_2, public_id=test_case_id_2
    )
    assert test_case_1 is not None
    assert test_case_2 is not None

    # assert test_case error is recorded
    test_case_1.state = TestStateEnum.CANCELLED
    test_case_2.state = TestStateEnum.PASSED


async def __run_exception_tests(db: Session) -> Tuple[TestSuite, TestCase]:
    runner, run, suite, case = await load_and_run_tool_unit_tests(
        db, TestSuiteExceptions, TCException
    )

    return suite, case
