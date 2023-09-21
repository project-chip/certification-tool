from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class SampleTestSuite2(TestSuite):
    metadata = {
        "public_id": "SampleTestSuite2",
        "version": "4.5.6",
        "title": "This is Test Suite 2 with version 4.5.6",
        "description": "This is Test Suite 2, it will not get a very long description",
    }

    async def setup(self) -> None:
        logger.info("This is a test setup")

    async def cleanup(self) -> None:
        logger.info("This is a test cleanup")
