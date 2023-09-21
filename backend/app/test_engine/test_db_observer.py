from datetime import datetime
from typing import Callable, Generator, Union

from loguru import logger
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.test_case_execution import TestCaseExecution
from app.models.test_enums import TestStateEnum
from app.models.test_run_execution import TestRunExecution
from app.models.test_step_execution import TestStepExecution
from app.models.test_suite_execution import TestSuiteExecution
from app.test_engine.models import TestCase, TestRun, TestStep, TestSuite
from app.test_engine.test_observer import Observer


class TestDBObserver(Observer):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    def __init__(
        self, db_generator: Callable[[], Generator[Session, None, None]] = get_db
    ) -> None:
        self.__db_generator = db_generator

    def dispatch(
        self, observable: Union[TestRun, TestSuite, TestCase, TestStep]
    ) -> None:
        logger.debug("Received Dispatch event")
        if observable is not None:
            if isinstance(observable, TestRun):
                self.__onTestRunUpdate(observable)
            elif isinstance(observable, TestSuite):
                self.__onTestSuiteUpdate(observable)
            elif isinstance(observable, TestCase):
                self.__onTestCaseUpdate(observable)
            elif isinstance(observable, TestStep):
                self.__onTestStepUpdate(observable)

    def __onTestRunUpdate(self, observable: "TestRun") -> None:
        logger.debug("Test Run Observer received", observable)
        test_run_execution = observable.test_run_execution
        test_run_execution.state = observable.state
        test_run_execution.log = observable.log

        if test_run_execution.started_at is None:
            test_run_execution.started_at = datetime.now()

        if self.isCompleted(observable.state):
            test_run_execution.completed_at = datetime.now()

        self.__save(test_run_execution)

    def __onTestSuiteUpdate(self, observable: "TestSuite") -> None:
        logger.debug("Test Suite Observer received", observable)
        if observable.test_suite_execution is not None:
            observable.test_suite_execution.state = observable.state
            if observable.errors:
                observable.test_suite_execution.errors = observable.errors

            if observable.test_suite_execution.started_at is None:
                observable.test_suite_execution.started_at = datetime.now()

            if self.isCompleted(observable.state):
                observable.test_suite_execution.completed_at = datetime.now()

            self.__save(observable.test_suite_execution)

    def __onTestCaseUpdate(self, observable: "TestCase") -> None:
        logger.debug("Test Case Observer received", observable)
        if observable.test_case_execution is not None:
            observable.test_case_execution.state = observable.state
            if observable.errors:
                observable.test_case_execution.errors = observable.errors

            if observable.test_case_execution.started_at is None:
                observable.test_case_execution.started_at = datetime.now()

            if self.isCompleted(observable.state):
                observable.test_case_execution.completed_at = datetime.now()

            self.__save(observable.test_case_execution)

    def __onTestStepUpdate(self, observable: "TestStep") -> None:
        logger.debug("Test Step Observer received", observable)
        if observable.test_step_execution is not None:
            observable.test_step_execution.state = observable.state
            if observable.errors:
                observable.test_step_execution.errors = observable.errors
            if observable.failures:
                observable.test_step_execution.failures = observable.failures

            if observable.test_step_execution.started_at is None:
                observable.test_step_execution.started_at = datetime.now()

            if self.isCompleted(observable.state):
                observable.test_step_execution.completed_at = datetime.now()

            self.__save(observable.test_step_execution)

    def __save(
        self,
        execution_obj: Union[
            TestCaseExecution, TestStepExecution, TestSuiteExecution, TestRunExecution
        ],
    ) -> None:
        # We get the session from the model it self to avoid overriding values when
        # using a different session
        insp = inspect(execution_obj)
        if insp is None or (session := insp.session) is None:
            logger.error(
                f"No Database session found for execution object: {execution_obj}."
            )
            session = next(self.__db_generator())
            session.add(execution_obj)
        session.expire_on_commit = False
        session.commit()
        logger.debug(
            f"Saved {execution_obj.__class__} {execution_obj.id}"
            f" with state {execution_obj.state}"
        )

    @staticmethod
    def isCompleted(state: TestStateEnum) -> bool:
        if state is not TestStateEnum.PENDING and state is not TestStateEnum.EXECUTING:
            return True
        else:
            return False
