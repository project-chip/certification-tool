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
from app.test_engine.models import TestSuite


class TestSuiteNeverEnding(TestSuite):
    metadata = {
        "public_id": "TestSuiteNeverEnding",
        "version": "1.2.3",
        "title": "A Test suite that can sleep forever. ",
        "description": "This is Test Suite that can sleep forever during all phases",
    }

    # Static variables to control exceptions
    never_end_during_setup = False  # type: bool
    never_end_during_cleanup = False  # type: bool

    async def setup(self) -> None:
        if self.never_end_during_setup:
            logger.info("Test Suite setup sleeping forever.")
            while True:
                await sleep(1)

    async def cleanup(self) -> None:
        if self.never_end_during_cleanup:
            logger.info("Test Suite cleanup sleeping forever.")
            while True:
                await sleep(1)
