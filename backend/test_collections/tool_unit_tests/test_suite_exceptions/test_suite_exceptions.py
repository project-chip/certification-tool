from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class SuiteSetupError(Exception):
    pass


class SuiteCleanupError(Exception):
    pass


class TestSuiteExceptions(TestSuite):
    metadata = {
        "public_id": "TestSuiteExceptions",
        "version": "1.2.3",
        "title": "A Test suite with custom exceptions",
        "description": "This is Test Suite that can cause exceptions during all phases",
    }

    # Static variables to control exceptions
    error_during_setup = True
    error_during_cleanup = True

    async def setup(self) -> None:
        if self.__class__.error_during_setup:
            logger.info("Test Suite setup error raised")
            raise SuiteSetupError("Error during setup")

    async def cleanup(self) -> None:
        if self.__class__.error_during_cleanup:
            logger.info("Test Suite cleanup error raised")
            raise SuiteCleanupError("Error during cleanup")
