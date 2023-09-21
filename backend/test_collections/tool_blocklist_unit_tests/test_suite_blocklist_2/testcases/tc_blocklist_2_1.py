from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCBlocklist21(TestCase):
    metadata = {
        "public_id": "TC_Blocklist_2_1",
        "version": "1.2.3",
        "title": "TC-Blocklist-2.1",
        "description": """This Test Case is built to test the test case blocklist,\
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
