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


class CaseSetupError(Exception):
    pass


class CaseExecuteError(Exception):
    pass


class CaseCleanupError(Exception):
    pass


class TCException(TestCase):
    metadata = {
        "public_id": "TCException",
        "version": "1.2.3",
        "title": "Test Case with errors",
        "description": "This Test case can cause errors at all levels",
    }

    # Static variables to control exceptions
    error_during_setup = True
    error_during_execute = True
    error_during_cleanup = True

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step Pass"),
            TestStep("Test Step Exception maybe"),
            TestStep("Test Step Pass"),
        ]

    async def setup(self) -> None:
        if self.__class__.error_during_setup:
            logger.info("Test Suite setup error raised")
            raise CaseSetupError("Error during setup")

    async def execute(self) -> None:
        # step 1 pass
        self.next_step()

        # step 2
        if self.__class__.error_during_execute:
            logger.info("Test Suite setup error raised")
            raise CaseExecuteError("Error during execute")

        self.next_step()

        # step 3 pass

    async def cleanup(self) -> None:
        if self.__class__.error_during_cleanup:
            logger.info("Test Suite cleanup error raised")
            raise CaseCleanupError("Error during cleanup")
