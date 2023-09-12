from asyncio import CancelledError
from typing import Any, List

from app.models import Project, TestCaseExecution
from app.models.test_enums import TestStateEnum
from app.schemas.test_environment_config import TestEnvironmentConfig
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.test_observable import TestObservable
from app.test_engine.test_observer import Observer

from .test_metadata import TestMetadata
from .test_step import TestStep


class TestCase(TestObservable):
    """
    TestCase is a run-time object for a test case
    """

    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    metadata: TestMetadata

    # TODO(#490): Need to be refactored to support real PIXIT format
    # Default test parameters are declared as class variables,
    # instance property will return runtime test_parameters.
    @classmethod
    def default_test_parameters(cls) -> dict[str, Any]:
        return {}

    @property
    def test_parameters(self) -> dict[str, Any]:
        if self.config.test_parameters is None:
            return self.default_test_parameters()
        else:
            all_test_parameters = (
                self.default_test_parameters() | self.config.test_parameters
            )

        # filter test_parameters to only contain relevant test_parameters from
        # default_test_parameters
        return {
            name: all_test_parameters[name]
            for name in self.default_test_parameters().keys()
        }

    def __init__(self, test_case_execution: TestCaseExecution):
        super().__init__()
        self.test_case_execution = test_case_execution
        self.current_test_step_index = 0
        self.test_steps: List[TestStep] = []
        self.create_test_steps()
        self.__state = TestStateEnum.PENDING
        self.errors: List[str] = []

    # Make pics a class method as they are mostly needed at class level.
    @classmethod
    def pics(cls) -> set[str]:
        return set()

    @property
    def project(self) -> Project:
        """Convenience getter to access project with settings.

        Returns:
            Project: project in which test case is being executed
        """
        return self.test_case_execution.test_suite_execution.test_run_execution.project

    @property
    def config(self) -> TestEnvironmentConfig:
        return self.project.config

    @property
    def state(self) -> TestStateEnum:
        return self.__state

    @state.setter
    def state(self, value: TestStateEnum) -> None:
        if self.__state != value:
            self.__state = value
            self.notify()

    def record_error(self, msg: str) -> None:
        self.errors.append(msg)
        logger.error(f"Test Case Error: {msg}")
        self.notify()

    def subscribe(self, observers: List[Observer]) -> None:
        super().subscribe(observers)
        self.__subscribe_test_steps(observers)

    def __subscribe_test_steps(self, observers: List[Observer]) -> None:
        for test_step in self.test_steps:
            test_step.subscribe(observers)

    def unsubscribe(self, observers: List[Observer]) -> None:
        super().unsubscribe(observers)
        self.__unsubscribe_test_steps(observers)

    def __unsubscribe_test_steps(self, observers: List[Observer]) -> None:
        for test_step in self.test_steps:
            test_step.unsubscribe(observers)

    @classmethod
    def public_id(cls) -> str:
        return cls.metadata["public_id"]

    @property
    def current_test_step(self) -> TestStep:
        return self.test_steps[self.current_test_step_index]

    def __compute_state(self) -> TestStateEnum:
        """
        State is computed based on test_case errors and test step state.
        """
        if self.errors is not None and len(self.errors) > 0:
            return TestStateEnum.ERROR

        # Cancelled is the only TS state that can cause a test case state to be
        # non-pending with pending test-steps.
        # Note: These loops cannot be easily coalesced as we need to iterate through
        # and assign Test Case State in order.
        if self.any_steps_with_state(TestStateEnum.ERROR):
            return TestStateEnum.ERROR

        if self.any_steps_with_state(TestStateEnum.FAILED):
            return TestStateEnum.FAILED

        if self.any_steps_with_state(TestStateEnum.CANCELLED):
            return TestStateEnum.CANCELLED

        if self.any_steps_with_state(TestStateEnum.PENDING):
            return TestStateEnum.PENDING

        return TestStateEnum.PASSED

    def any_steps_with_state(self, state: TestStateEnum) -> bool:
        return any(ts for ts in self.test_steps if ts.state == state)

    def completed(self) -> bool:
        return self.state not in [TestStateEnum.PENDING, TestStateEnum.EXECUTING]

    def cancel(self) -> None:
        # Only cancel if test case is not already completed
        if self.completed():
            return

        logger.info("Cancel test case")
        self.state = TestStateEnum.CANCELLED

        # Cancel remaning test_steps
        for step in self.test_steps:
            step.cancel()

    def mark_as_completed(self) -> None:
        if self.completed():
            return
        self.state = self.__compute_state()
        logger.info(f"Test Case Completed[{self.state.name}]: {self.metadata['title']}")

    def mark_as_executing(self) -> None:
        self.state = TestStateEnum.EXECUTING
        logger.info(f"Executing Test Case: {self.metadata['title']}")

    ###
    # Running with error handling
    ###
    async def run(self) -> None:
        self.mark_as_executing()
        if await self.__setup_catch_errors():
            await self.__execute_catch_errors()

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

        # All other exceptions will cause test case error immediately
        except Exception as e:
            error = (
                "Error occurred during setup of test case "
                + f"{self.metadata['public_id']}. {e}"
            )
            self.record_error(error)
            return False

    async def __execute_catch_errors(self) -> None:
        try:
            # We need to mark the first test step as executing, as self.execute() will
            # only handle the step transitions.
            self.current_test_step.mark_as_executing()
            await self.execute()

        # CancelledError needs to be raised again, as it is handled in the runner
        except CancelledError:
            self.cancel()  # This will as set current_test_step as cancelled
            # if cancelled during execute we still call cleanup()
            await self.__cleanup_catch_errors()
            raise

        # All other exceptions will cause test case error immediately
        except Exception as e:
            error = (
                "Error occurred during execution of test case "
                + f"{self.metadata['public_id']}. {e}"
            )
            # Record error on test_step during execute
            self.current_test_step.record_error(error)

        # Always mark the last step as completed.
        finally:
            self.current_test_step.mark_as_completed()

    async def __cleanup_catch_errors(self) -> None:
        try:
            await self.cleanup()

        # CancelledError needs to be raised again, as it is handled in the runner
        except CancelledError:
            self.cancel()
            raise

        # All other exceptions will cause test case error immediately
        except Exception as e:
            error = (
                "Error occurred during cleanup of test case "
                + f"{self.metadata['public_id']}. {e}"
            )
            self.record_error(error)

    ###
    # Helpers
    ###

    def mark_step_failure(self, msg: str) -> None:
        self.current_test_step.append_failure(msg)

    def next_step(self) -> None:
        if self.current_test_step_index + 1 >= len(self.test_steps):
            return

        # mark old step as complete
        old_step = self.current_test_step
        if old_step.state == TestStateEnum.EXECUTING:
            old_step.mark_as_completed()

        # update current step
        self.current_test_step_index += 1
        self.current_test_step.mark_as_executing()

    ###
    # Below is expected to be overridden by each test script
    ###
    def create_test_steps(self) -> None:
        raise NotImplementedError  # Must be overridden by subclass

    async def setup(self) -> None:
        raise NotImplementedError  # Must be overridden by subclass

    async def execute(self) -> None:
        raise NotImplementedError  # Must be overridden by subclass

    async def cleanup(self) -> None:
        raise NotImplementedError  # Must be overridden by subclass
