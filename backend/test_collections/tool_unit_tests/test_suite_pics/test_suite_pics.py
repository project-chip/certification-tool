from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class TestPICSSuite(TestSuite):
    metadata = {
        "public_id": "TestPICSSuite",
        "version": "1.2.3",
        "title": "Test Suite TestPICSSuite",
        "description": " Test suite for testing PICS",
    }

    async def setup(self) -> None:
        logger.info("This is a PICS test suite setup.")

    async def cleanup(self) -> None:
        logger.info("This is a PICS test suite cleanup.")
