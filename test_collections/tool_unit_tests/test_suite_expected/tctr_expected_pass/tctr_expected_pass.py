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
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCTRExpectedPass(TestCase):
    metadata = {
        "public_id": "TCTRExpectedPass",
        "version": "1.2.3",
        "title": "This is Test Case tctr_expected_pass",
        "description": """This Test Case is built to test the test runner,\
             it is supposed to pass""",
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
            logger.info("Executing something in" + step.name)
            self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
