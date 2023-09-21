from app.chip_tool.chip_tool import ChipToolTestType
from app.chip_tool.test_case import ChipToolTest
from app.default_environment_config import default_environment_config
from app.schemas.test_environment_config import TestEnvironmentConfig
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep


class TCTRChipToolLogParsing(ChipToolTest):
    metadata = {
        "public_id": " TCTRChipToolLogParsing",
        "version": "1.2.3",
        "title": "This is Test Case tctr_chip_tool_log_parsing",
        "description": "This Test Case is built to test the chip-tool log parser",
    }
    test_type = ChipToolTestType.CHIP_APP
    chip_tool_test_identifier = "Test ID"

    # The config() defined in the "TestCase" base class is unable to return a valid
    # value because the attributes - test_suite_execution, test_run_execution and
    # project are not set up. So, override the base class config() to return the
    # default config.
    @property
    def config(self) -> TestEnvironmentConfig:
        return default_environment_config.copy(deep=True)

    def create_test_steps(self) -> None:
        self.test_steps = [TestStep("Test Step 1")]
        self.test_steps = [TestStep("Test Step 2")]
        self.test_steps = [TestStep("Test Step 3")]

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
