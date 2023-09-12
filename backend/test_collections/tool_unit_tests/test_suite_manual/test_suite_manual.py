"""Manual Test Suite Unit Test."""

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class TestSuiteManual(TestSuite):
    metadata = {
        "public_id": "TestSuiteManual",
        "version": "1.2.3",
        "title": "A Manual Test Suite",
        "description": "This is Test Suite that must be executed manually.",
    }

    async def setup(self) -> None:
        logger.info("This is a MANUAL test suite setup.")

    async def cleanup(self) -> None:
        logger.info("This is a MANUAL test suite cleanup.")
