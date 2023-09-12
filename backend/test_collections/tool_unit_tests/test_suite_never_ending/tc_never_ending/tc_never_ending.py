import asyncio

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCNeverEnding(TestCase):
    metadata = {
        "public_id": "TCNeverEnding",
        "version": "1.2.3",
        "title": "Test Case that can sleep forever",
        "description": "This Test case is built to test the test"
        "runner's ability to handle CancelledError.",
    }

    # Static variables to control exceptions
    never_end_during_setup = False  # type: bool
    never_end_during_execute = False  # type: bool
    never_end_during_cleanup = False  # type: bool

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step Pass"),
            TestStep("Test Step Sleep Infinitely Maybe"),
            TestStep("Test Step Pass"),
        ]

    async def setup(self) -> None:
        if self.never_end_during_setup:
            logger.info("Test Case setup sleeping forever.")
            while True:
                await asyncio.sleep(1)

    async def execute(self) -> None:
        self.next_step()
        if self.never_end_during_execute:
            logger.info("Test Case execute sleeping forever.")
            while True:
                await asyncio.sleep(1)
        self.next_step()

    async def cleanup(self) -> None:
        if self.never_end_during_cleanup:
            logger.info("Test Case cleanup sleeping forever.")
            while True:
                await asyncio.sleep(1)
