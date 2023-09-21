import asyncio
from typing import Tuple

import pytest
from sqlalchemy.orm import Session

from app.models.test_enums import TestStateEnum
from app.test_engine.test_runner import TestRunner
from app.tests.utils.test_runner import (
    get_test_case_for_public_id,
    get_test_suite_for_public_id,
    load_test_run_for_test_cases,
)
from test_collections.tool_unit_tests.test_suite_never_ending import (
    TestSuiteNeverEnding,
)
from test_collections.tool_unit_tests.test_suite_never_ending.tc_never_ending import (
    TCNeverEnding,
)


@pytest.mark.asyncio
async def test_abort_suite_setup(db: Session) -> None:
    test_suite, test_case = __load_abort_tests(db)
    test_suite.never_end_during_setup = True
    await __run_abort_tests()

    assert test_suite.state is TestStateEnum.CANCELLED
    assert len(test_suite.errors) == 0

    assert test_case.state == TestStateEnum.CANCELLED
    assert len(test_case.errors) == 0

    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_abort_suite_cleanup(db: Session) -> None:
    test_suite, test_case = __load_abort_tests(db)
    test_suite.never_end_during_cleanup = True
    await __run_abort_tests()

    assert test_suite.state == TestStateEnum.CANCELLED
    assert len(test_suite.errors) == 0

    assert test_case.state == TestStateEnum.PASSED
    assert len(test_case.errors) == 0

    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.PASSED


@pytest.mark.asyncio
async def test_abort_case_setup(db: Session) -> None:
    test_suite, test_case = __load_abort_tests(db)
    test_case.never_end_during_setup = True
    await __run_abort_tests()

    assert test_suite.state == TestStateEnum.CANCELLED
    assert len(test_suite.errors) == 0

    assert test_case.state == TestStateEnum.CANCELLED
    assert len(test_case.errors) == 0

    assert len(test_case.test_steps) == 3
    for step in test_case.test_steps:
        assert step.state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_abort_case_execution(db: Session) -> None:
    test_suite, test_case = __load_abort_tests(db)
    test_case.never_end_during_execute = True
    await __run_abort_tests()

    assert test_suite.state == TestStateEnum.CANCELLED
    assert len(test_suite.errors) == 0

    assert test_case.state == TestStateEnum.CANCELLED
    assert len(test_case.errors) == 0

    assert len(test_case.test_steps) == 3
    assert test_case.test_steps[0].state == TestStateEnum.PASSED
    assert test_case.test_steps[1].state == TestStateEnum.CANCELLED
    assert test_case.test_steps[2].state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_abort_case_cleanup(db: Session) -> None:
    test_suite, test_case = __load_abort_tests(db)
    test_case.never_end_during_cleanup = True
    await __run_abort_tests()

    assert test_suite.state == TestStateEnum.CANCELLED
    assert len(test_suite.errors) == 0

    assert test_case.state == TestStateEnum.CANCELLED
    assert len(test_case.errors) == 0

    assert len(test_case.test_steps) == 3
    assert test_case.test_steps[0].state == TestStateEnum.PASSED
    assert test_case.test_steps[1].state == TestStateEnum.PASSED
    assert test_case.test_steps[2].state == TestStateEnum.PASSED


def __load_abort_tests(db: Session) -> Tuple[TestSuiteNeverEnding, TCNeverEnding]:
    test_suite_id = "TestSuiteNeverEnding"
    test_case_id = "TCNeverEnding"
    selected_tests = {"tool_unit_tests": {test_suite_id: {test_case_id: 1}}}
    test_runner = load_test_run_for_test_cases(db=db, test_cases=selected_tests)
    run = test_runner.test_run
    assert run is not None

    test_suite = get_test_suite_for_public_id(test_run=run, public_id=test_suite_id)
    assert test_suite is not None
    assert isinstance(test_suite, TestSuiteNeverEnding)

    test_case = get_test_case_for_public_id(
        test_suite=test_suite, public_id=test_case_id
    )
    assert test_case is not None
    assert isinstance(test_case, TCNeverEnding)

    return test_suite, test_case


async def __run_abort_tests() -> None:
    runner = TestRunner()
    run_task = asyncio.create_task(runner.run())
    await asyncio.sleep(1)
    runner.abort_testing()
    await run_task
