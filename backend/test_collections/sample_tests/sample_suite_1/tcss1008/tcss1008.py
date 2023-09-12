from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCSS1008(TestCase):
    metadata = {
        "public_id": "TCSS1008",
        "version": "1.2.3",
        "title": "This is Test Case tcss1008",
        "description": """This is Test Case tcss1008,\
        it will not get a very long description""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step 1"),
            TestStep("Test Step 2"),
            TestStep("Test Step 3"),
            TestStep("Test Step 4"),
            TestStep("Test Step 5"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        for i in range(1, 5):
            logger.info("Executing something in Step {}".format(i))
            self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
