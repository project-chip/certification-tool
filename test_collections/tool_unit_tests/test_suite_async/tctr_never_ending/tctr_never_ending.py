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
from asyncio import sleep

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCTRNeverEnding(TestCase):
    metadata = {
        "public_id": "TCTRNeverEnding",
        "version": "1.2.3",
        "title": "This is Test Case tctr_never_ending",
        "description": """This Test Case is built to test the test runner,\
             step 2 is supposed to run for ever""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("No-op"),
            TestStep("Run forever"),
            TestStep("Not reachable"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        logger.info("This is a test step 1: No-op")
        self.next_step()
        logger.info("This is a test step 2: sleep for ever")
        while True:
            await sleep(1)

        # We know this is unreachable, but it still makes sense for unit testing
        self.next_step()  # type: ignore
        logger.info("This is a test step 3: we will never get here")

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
