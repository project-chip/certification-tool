from asyncio import CancelledError, sleep
from typing import List, Optional, Type

from app.models import Project, TestSuiteExecution
from app.models.test_enums import TestStateEnum
from app.schemas.pics import PICS
from app.schemas.test_environment_config import TestEnvironmentConfig
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.test_observable import TestObservable
from app.test_engine.test_observer import Observer

from .test_case import TestCase
from .test_metadata import TestMetadata


class TestSuite(TestObservable):
    """
    Test suite is a run-time object for a test_suite
    """

    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    metadata: TestMetadata

    available_test_cases: List[Type[TestCase]] = []

    def __init__(self, test_suite_execution: TestSuiteExecution):
        super().__init__()
        self.test_suite_execution: TestSuiteExecution = test_suite_execution
        self.current_test_case: Optional[TestCase] = None
        self.test_cases: List[TestCase] = []
        self.__state = TestStateEnum.PENDING
        self.errors: List[str] = []

    @property
    def project(self) -> Project:
        """Convenience getter to access project with settings.

        Returns:
            Project: project in which test suite is being executed
        """
        return self.test_suite_execution.test_run_execution.project

    @property
    def config(self) -> TestEnvironmentConfig:
        return self.project.config

    @property
    def pics(self) -> PICS:
        return PICS.parse_obj(self.project.pics)

    @property
    def state(self) -> TestStateEnum:
        return self.__state

    @state.setter
    def state(self, value: TestStateEnum) -> None:
        if self.__state != value:
            self.__state = value
            self.notify()

    def __compute_state(self) -> TestStateEnum:
        """
        State is computed based test_suite errors and on on test case states.
        """
        if self.errors is not None and len(self.errors) > 0:
            return TestStateEnum.ERROR

        # Cancelled is the only TC state that can cause a test suite state to be
        # non-pending with pending test-steps.
        # Note: These loops cannot be easily coalesced as we need to iterate through
        # and assign Test Suite State in order.
        if any(tc for tc in self.test_cases if tc.state == TestStateEnum.ERROR):
            return TestStateEnum.ERROR

        if any(tc for tc in self.test_cases if tc.state == TestStateEnum.FAILED):
            return TestStateEnum.FAILED

        if any(tc for tc in self.test_cases if tc.state == TestStateEnum.CANCELLED):
            return TestStateEnum.CANCELLED

        if any(tc for tc in self.test_cases if tc.state == TestStateEnum.PENDING):
            return TestStateEnum.PENDING

        return TestStateEnum.PASSED

    def completed(self) -> bool:
        return self.state not in [TestStateEnum.PENDING, TestStateEnum.EXECUTING]

    def cancel(self) -> None:
        # Only cancel if test suite is not already completed
        if self.completed():
            return

        logger.info("Cancel test suite")
        self.state = TestStateEnum.CANCELLED

        self.cancel_remaining_tests()

    def cancel_remaining_tests(self) -> None:
        # Cancel remaning test_cases
        for test_case in self.test_cases:
            test_case.cancel()

    def mark_as_completed(self) -> None:
        if self.completed():
            return
        self.state = self.__compute_state()
        logger.info(
            f"Test Suite Completed [{self.state.name}]: {self.metadata['title']}"
        )

    def mark_as_executing(self) -> None:
        self.state = TestStateEnum.EXECUTING
        logger.info(f"Test Suite Executing: {self.metadata['title']}")

    def record_error(self, msg: str) -> None:
        self.errors.append(msg)
        logger.error(f"Test Suite Error: {msg}")
        self.notify()

    #######
    # Running with error handling
    #######
    async def run(self) -> None:
        self.mark_as_executing()

        if len(self.test_cases) == 0:
            logger.warning("Test Case list is empty, please select a test case")
        else:
            # Only run tests if setup is successful
            if await self.__setup_catch_errors():
                await self.__run_test_cases()

            # always run test suite clean up
            await self.__cleanup_catch_errors()

        self.mark_as_completed()

    async def __setup_catch_errors(self) -> bool:
        try:
            await self.setup()
            return True

        # CancelledError needs to be raised again, as it is handled in the runner
        except CancelledError:
            self.cancel()
            # if cancelled during setup we still call cleanup()
            await self.__cleanup_catch_errors()
            raise

        # All other exceptions will cause test suite error immediately
        except Exception as e:
            error = (
                "Error occurred during setup of test suite."
                + f"{self.metadata['public_id']}. {e}"
            )
            self.record_error(error)
            # Cancel test cases in test suite
            self.cancel_remaining_tests()
            return False

    async def __run_test_cases(self) -> None:
        # TODO: __current_test_suite should never be non here, but we should raise
        for test_case in self.test_cases:
            await self.__run_test_catch_errors(test_case)

            # We yield the run loop after each test case,
            # just in case others are waiting for it. This shouldn't be needed, but if
            # several test cases in a row has a lot of non-async code, we could be
            # blocking the run-loop.
            # See https://docs.python.org/3.10/library/asyncio-task.html#sleeping
            await sleep(0)

    async def __run_test_catch_errors(self, test_case: TestCase) -> None:
        try:
            self.current_test_case = test_case
            await test_case.run()

        # All other exceptions will cause test case to error immediately
        except CancelledError:
            self.cancel()
            # if cancelled during test case we still call cleanup()
            await self.__cleanup_catch_errors()
            raise
        finally:
            self.current_test_case = None

    async def __cleanup_catch_errors(self) -> None:
        try:
            await self.cleanup()

        # CancelledError needs to be raised again, as it is handled in the runner
        except CancelledError:
            self.cancel()
            raise

        # All other exceptions will cause test suite error immediately
        except Exception as e:
            error = (
                "Error occurred during cleanup of test suite "
                + f"{self.metadata['public_id']}. {e}"
            )
            self.record_error(error)

    ########
    # Subscribe/Unsubscribe Observer
    ########
    def subscribe(self, observers: List[Observer]) -> None:
        super().subscribe(observers)
        self.__subscribe_test_cases(observers)

    def __subscribe_test_cases(self, observers: List[Observer]) -> None:
        for test_case in self.test_cases:
            test_case.subscribe(observers)

    def unsubscribe(self, observers: List[Observer]) -> None:
        super().unsubscribe(observers)
        self.__unsubscribe_test_cases(observers)

    def __unsubscribe_test_cases(self, observers: List[Observer]) -> None:
        for test_case in self.test_cases:
            test_case.unsubscribe(observers)

    @classmethod
    def public_id(cls) -> str:
        return cls.metadata["public_id"]

    # To be overridden
    async def setup(self) -> None:
        logger.info("`setup` not implemented in test suite")

    # To be overridden
    async def cleanup(self) -> None:
        logger.info("`cleanup` not implemented in test suite")
