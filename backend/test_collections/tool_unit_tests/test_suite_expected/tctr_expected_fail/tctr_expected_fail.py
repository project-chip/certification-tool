from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCTRExpectedFail(TestCase):
    metadata = {
        "public_id": "TCTRExpectedFail",
        "version": "1.2.3",
        "title": "This is Test Case tctr_expected_fail",
        "description": """This Test Case is built to test the test runner,\
             it is supposed to fail""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step 1"),
            TestStep("Test Step 2"),
            TestStep("Test Step 3"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        for step in self.test_steps:
            if step.name == "Test Step 2":
                self.mark_step_failure("Failed Test Step 2")
            self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
