from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class SampleTestSuite1(TestSuite):
    metadata = {
        "public_id": "SampleTestSuite1",
        "version": "1.2.3",
        "title": "This is Test Suite 1",
        "description": "This is Test Suite 1, it will not get a very long description",
    }

    async def setup(self) -> None:
        logger.info("This is a test setup")

    async def cleanup(self) -> None:
        logger.info("This is a test cleanup")
