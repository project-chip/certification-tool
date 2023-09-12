from asyncio import sleep

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class TestSuiteNeverEnding(TestSuite):
    metadata = {
        "public_id": "TestSuiteNeverEnding",
        "version": "1.2.3",
        "title": "A Test suite that can sleep forever. ",
        "description": "This is Test Suite that can sleep forever during all phases",
    }

    # Static variables to control exceptions
    never_end_during_setup = False  # type: bool
    never_end_during_cleanup = False  # type: bool

    async def setup(self) -> None:
        if self.never_end_during_setup:
            logger.info("Test Suite setup sleeping forever.")
            while True:
                await sleep(1)

    async def cleanup(self) -> None:
        if self.never_end_during_cleanup:
            logger.info("Test Suite cleanup sleeping forever.")
            while True:
                await sleep(1)
