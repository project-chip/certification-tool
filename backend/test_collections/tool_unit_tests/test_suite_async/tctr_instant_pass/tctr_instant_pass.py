from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCTRInstantPass(TestCase):
    metadata = {
        "public_id": "TCTRInstantPass",
        "version": "1.2.3",
        "title": "This is Test Case tctr_instant_pass",
        "description": """This Test Case is built to test the test runner,\
             it is supposed pass instantly""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [TestStep("Test Step 1")]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        pass

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
