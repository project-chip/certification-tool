from typing import Optional, Tuple, Type

from sqlalchemy.orm import Session

from app.schemas import TestSelection
from app.schemas.test_runner_status import TestRunnerState
from app.test_engine.models import TestCase, TestRun, TestSuite
from app.test_engine.test_runner import TestRunner
from app.tests.utils.test_run_execution import create_random_test_run_execution


def get_test_case_for_public_id(
    test_suite: TestSuite, public_id: str
) -> Optional[TestCase]:
    return next(
        (
            test_case
            for test_case in test_suite.test_cases
            if test_case.public_id() == public_id
        ),
        None,
    )


def get_test_suite_for_public_id(
    test_run: TestRun, public_id: str
) -> Optional[TestSuite]:
    return next(
        (
            test_suite
            for test_suite in test_run.test_suites
            if test_suite.public_id() == public_id
        ),
        None,
    )


def load_test_run_for_test_cases(db: Session, test_cases: TestSelection) -> TestRunner:
    test_run_execution = create_random_test_run_execution(
        db=db, selected_tests=test_cases
    )
    # Get TestRunner (singleton)
    test_runner = TestRunner()

    # Ensure initial state is IDLE
    assert test_runner.state == TestRunnerState.IDLE
    test_runner.load_test_run(test_run_execution.id)
    return test_runner


async def load_and_run_tool_unit_tests(
    db: Session,
    suite_cls: Type[TestSuite],
    case_cls: Type[TestCase],
    iterations: int = 1,
) -> Tuple[TestRunner, TestRun, TestSuite, TestCase]:
    selected_tests = {
        "tool_unit_tests": {suite_cls.public_id(): {case_cls.public_id(): iterations}}
    }
    runner = load_test_run_for_test_cases(db=db, test_cases=selected_tests)
    run = runner.test_run
    assert run is not None

    assert len(run.test_suites) == 1
    suite = run.test_suites[0]

    assert len(suite.test_cases) == iterations
    case = suite.test_cases[0]

    await runner.run()

    return runner, run, suite, case
