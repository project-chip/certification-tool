from typing import Callable, Generator, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.models import TestRunExecution, TestStateEnum
from app.schemas.test_runner_status import TestRunnerState
from app.singleton import Singleton
from app.test_engine import (
    TEST_ENGINE_BUSY_MESSAGE,
    TEST_ENGINE_NOT_ACTIVE_MESSAGE,
    TEST_RUN_ALREADY_EXECUTED_MESSAGE,
)
from app.test_engine.logger import test_engine_logger
from app.test_engine.test_db_observer import TestDBObserver
from app.test_engine.test_log_handler import TestLogHandler
from app.test_engine.test_script_manager import TestNotFound, test_script_manager
from app.test_engine.test_ui_observer import TestUIObserver
from app.user_prompt_support import UploadedFileSupport, UploadFile
from app.version import version_information

from .models import TestRun


class LoadingError(Exception):
    """Raised when errors happend while loading a test run."""


class AbortError(Exception):
    """Raised when errors happend while aborting a test run."""


# Test runner is a Singleton, we're implementing all methods directly in this module.
class TestRunner(object, metaclass=Singleton):
    __test__ = False

    def __init__(
        self, db_generator: Callable[[], Generator[Session, None, None]] = get_db
    ) -> None:
        self.__state = TestRunnerState.IDLE
        self.test_run: Optional[TestRun] = None
        self.__db_generator = db_generator
        self.__db = next(self.__db_generator())

    # State is read only publicly
    @property
    def state(self) -> TestRunnerState:
        return self.__state

    # LOADING new test run
    def load_test_run(self, test_run_execution_id: int) -> None:
        """This will load all the tests for an given test_run.

        The input is based on id, instead of the record directly to avoid database
        models belonging to different DB sessions


        Args:
            test_run_execution_id (int): id of the test run to load
        """
        # TODO: Better error handling
        if self.state != TestRunnerState.IDLE:
            raise LoadingError(TEST_ENGINE_BUSY_MESSAGE)

        self.__state = TestRunnerState.LOADING
        # New DB session is required to avoid any cached session.
        self.__reset_db_session()

        try:
            # Load test_run_execution
            test_run_execution = self.__fetch_test_run_execution(test_run_execution_id)
            logger.info(f"Loading Test Run: {test_run_execution.title}")

            # Load test_run
            logger.info(f"Loading Test Run: {test_run_execution.title}")
            self.test_run = test_script_manager.get_test_run(
                self.__db, test_run_execution
            )
        except (LoadingError, TestNotFound):
            self.__state = TestRunnerState.IDLE
            raise

        self.__state = TestRunnerState.READY
        logger.info("Test Runner is Ready")

    def __fetch_test_run_execution(self, id: int) -> TestRunExecution:
        test_run_execution = crud.test_run_execution.get(db=self.__db, id=id)
        if test_run_execution is None:
            raise LoadingError(
                f"No test run execution with id ({id}) found in database"
            )

        if test_run_execution.state is not TestStateEnum.PENDING:
            raise LoadingError(TEST_RUN_ALREADY_EXECUTED_MESSAGE)
        self.test_run_execution = test_run_execution
        return test_run_execution

    def abort_testing(self) -> None:
        if self.state is TestRunnerState.IDLE:
            raise AbortError(TEST_ENGINE_NOT_ACTIVE_MESSAGE)

        if self.state is TestRunnerState.READY:
            self.__cleanup_run()
            return

        if self.state is TestRunnerState.RUNNING:
            if self.test_run is None:
                raise AbortError(TEST_ENGINE_NOT_ACTIVE_MESSAGE)

            self.test_run.cancel()

    def handle_uploaded_file(self, file: UploadFile) -> None:
        if self.test_run is None:
            raise AttributeError(TEST_ENGINE_NOT_ACTIVE_MESSAGE)
        if self.test_run.current_test_suite is None:
            raise AttributeError(
                "There is no active test suite to handle the uploaded file."
            )
        if self.test_run.current_test_suite.current_test_case is None:
            raise AttributeError(
                "There is no active test case to handle the uploaded file."
            )
        current_test_case = self.test_run.current_test_suite.current_test_case
        if isinstance(current_test_case, UploadedFileSupport):
            current_test_case.handle_uploaded_file(file=file)
        else:
            raise AttributeError(
                "The current test case has no way to handle the uploaded file."
                "It is missing a handle_uploaded_file() implementation."
            )

    async def run(self) -> None:
        # TODO: Better error handling
        if self.state != TestRunnerState.READY:
            logger.error("Test Runner not ready to run")
            return

        if self.test_run is None:
            logger.error("Test Run is not loaded")
            return

        log_handler = TestLogHandler(self.test_run)
        test_engine_logger.info("Run Test Runner is Ready")
        test_engine_logger.info(f"TH Version: {version_information.version}")
        test_engine_logger.info(f"TH SHA: {version_information.sha}")
        test_engine_logger.info(f"TH SDK SHA: {version_information.sdk_sha}")

        # Execute each test suite asynchronously
        self.__state = TestRunnerState.RUNNING

        # Init new observers
        ui_observer = TestUIObserver()
        db_observer = TestDBObserver(self.__db_generator)
        self.test_run.subscribe([ui_observer, db_observer])

        await self.test_run.run()

        # Ensure all log messages are sent out
        await log_handler.finish()

        self.test_run.unsubscribe([ui_observer, db_observer])

        # Ensure all state updates are sent to the frontend
        await ui_observer.complete_tasks()

        self.__cleanup_run()

    def __cleanup_run(self) -> None:
        self.test_run = None
        self.__state = TestRunnerState.IDLE

    def __reset_db_session(self) -> None:
        if self.__db is not None:
            self.__db.close()
        self.__db = next(self.__db_generator())
