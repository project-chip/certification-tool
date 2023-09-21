from asyncio import CancelledError, Task, create_task
from typing import List, Optional

from app.models import Project, TestRunExecution
from app.models.test_enums import TestStateEnum
from app.schemas.test_environment_config import TestEnvironmentConfig
from app.schemas.test_run_log_entry import TestRunLogEntry
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.test_observable import TestObservable
from app.test_engine.test_observer import Observer

from .test_suite import TestSuite


class TestRun(TestObservable):
    """
    Test run is a run-time object for a test_run
    """

    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    def __init__(self, test_run_execution: TestRunExecution):
        super().__init__()
        self.test_run_execution = test_run_execution
        self.current_test_suite: Optional[TestSuite] = None
        self.test_suites: List[TestSuite] = []
        self.__state = TestStateEnum.PENDING
        self.__current_testing_task: Optional[Task] = None
        self.log: list[TestRunLogEntry] = []

    @property
    def project(self) -> Project:
        """Convenience getter to access project.

        Returns:
            Project: project in which test run is being executed
        """
        return self.test_run_execution.project

    @property
    def config(self) -> TestEnvironmentConfig:
        """Convenience getter to access project config."""
        return self.project.config

    @property
    def state(self) -> TestStateEnum:
        return self.__state

    @state.setter
    def state(self, value: TestStateEnum) -> None:
        if self.__state != value:
            self.__state = value
            self.notify()

    def __compute_state(self) -> TestStateEnum:
        """State computed based test_suite states."""

        # Cancelled is the only TS state that can cause a test run state to be
        # non-pending with pending test-steps.
        # Note: These loops cannot be easily coalesced as we need to iterate through
        # and assign Test Suite State in order.
        if any(ts for ts in self.test_suites if ts.state == TestStateEnum.ERROR):
            return TestStateEnum.ERROR

        if any(ts for ts in self.test_suites if ts.state == TestStateEnum.FAILED):
            return TestStateEnum.FAILED

        if any(ts for ts in self.test_suites if ts.state == TestStateEnum.CANCELLED):
            return TestStateEnum.CANCELLED

        if any(ts for ts in self.test_suites if ts.state == TestStateEnum.PENDING):
            return TestStateEnum.PENDING

        return TestStateEnum.PASSED

    def completed(self) -> bool:
        return self.state not in [TestStateEnum.PENDING, TestStateEnum.EXECUTING]

    def mark_as_completed(self) -> None:
        if self.completed():
            return
        self.state = self.__compute_state()
        logger.info(f"Test Run Completed [{self.state.name}]")

    def mark_as_executing(self) -> None:
        self.state = TestStateEnum.EXECUTING
        logger.info("Test Run Executing")

    async def run(self) -> None:
        """Perform the test run, by executing test suites one at a time."""
        self.mark_as_executing()

        for test_suite in self.test_suites:
            try:
                self.current_test_suite = test_suite
                self.__current_testing_task = create_task(test_suite.run())
                await self.__current_testing_task
            except CancelledError:
                logger.error("User cancelled test run")
                self.state = TestStateEnum.CANCELLED
                self.__cancel_remaining_tests()
                break
            finally:
                self.__current_testing_task = None
                self.current_test_suite = None
                self.mark_as_completed()

    def cancel(self) -> None:
        """This will abort executuion of the current test suite, and mark all remaining
        tests as cancelled."""
        if self.__current_testing_task is None:
            logger.error("Cannot cancel test run when no test is running")
            return

        logger.error("User cancelled test run")
        self.__current_testing_task.cancel()
        self.__current_testing_task = None

    def __cancel_remaining_tests(self) -> None:
        """This will cancel all remaining test suites, and it's test cases."""
        for test_suite in self.test_suites:
            # Note: cancel on a completed test_suite is a No-op
            test_suite.cancel()

    def append_log_entries(self, entries: list[TestRunLogEntry]) -> None:
        self.log.extend(entries)
        self.notify()

    def subscribe(self, observers: List[Observer]) -> None:
        """Subscribe a list of observers to test run changes, and changes on sub-models
        test suites, test cases, and test steps.

        Args:
            observers (List[Observer]): Observers to be notified of changes
        """
        super().subscribe(observers)
        self.__subscribe_test_suites(observers)

    def __subscribe_test_suites(self, observers: List[Observer]) -> None:
        """Subscribe sub-models to observers

        Args:
            observers (List[Observer]): Observers to be notified of changes
        """
        for test_suite in self.test_suites:
            test_suite.subscribe(observers)

    def unsubscribe(self, observers: List[Observer]) -> None:
        """Unsubscribe observers from changes to test run changes, and sub-models
        test suites, test cases, and test steps.

        Args:
            observers (List[Observer]): Observers to be unsubscribed
        """
        super().unsubscribe(observers)
        self.__unsubscribe_test_suites(observers)

    def __unsubscribe_test_suites(self, observers: List[Observer]) -> None:
        """Unsubscribe sub-models to observers

        Args:
            observers (List[Observer]): Observers to be unsubscribed
        """
        for test_suite in self.test_suites:
            test_suite.unsubscribe(observers)
