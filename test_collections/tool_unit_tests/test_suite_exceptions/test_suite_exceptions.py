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
from app.test_engine.models import TestSuite


class SuiteSetupError(Exception):
    pass


class SuiteCleanupError(Exception):
    pass


class TestSuiteExceptions(TestSuite):
    metadata = {
        "public_id": "TestSuiteExceptions",
        "version": "1.2.3",
        "title": "A Test suite with custom exceptions",
        "description": "This is Test Suite that can cause exceptions during all phases",
    }

    # Static variables to control exceptions
    error_during_setup = True
    error_during_cleanup = True

    async def setup(self) -> None:
        if self.__class__.error_during_setup:
            logger.info("Test Suite setup error raised")
            raise SuiteSetupError("Error during setup")

    async def cleanup(self) -> None:
        if self.__class__.error_during_cleanup:
            logger.info("Test Suite cleanup error raised")
            raise SuiteCleanupError("Error during cleanup")
