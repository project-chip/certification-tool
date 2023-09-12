from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class TestSuiteExpected(TestSuite):
    metadata = {
        "public_id": "TestSuiteExpected",
        "version": "1.2.3",
        "title": "This is Test Runner Test Suite",
        "description": "This is Test Runner Test Suite",
    }

    async def setup(self) -> None:
        logger.info("This is a test setup")

    async def cleanup(self) -> None:
        logger.info("This is a test cleanup")
