#
# Copyright (c) 2023 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from app.default_environment_config import default_environment_config
from app.schemas.test_environment_config import TestEnvironmentConfig
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep
from test_collections.matter.sdk_tests.support.chip.chip_server import ChipServerType
from test_collections.matter.sdk_tests.support.yaml_tests.models.chip_test import (
    ChipTest,
)


class TCTRChipLogParsing(ChipTest):
    metadata = {
        "public_id": " TCTRChipLogParsing",
        "version": "1.2.3",
        "title": "This is Test Case tctr_chip_log_parsing",
        "description": "This Test Case is built to test the chip-tool log parser",
    }
    server_type = ChipServerType.CHIP_APP
    chip_test_identifier = "Test ID"

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
