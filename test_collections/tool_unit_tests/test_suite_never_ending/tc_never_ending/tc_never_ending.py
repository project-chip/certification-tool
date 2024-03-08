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
import asyncio

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep


class TCNeverEnding(TestCase):
    metadata = {
        "public_id": "TCNeverEnding",
        "version": "1.2.3",
        "title": "Test Case that can sleep forever",
        "description": "This Test case is built to test the test"
        "runner's ability to handle CancelledError.",
    }

    # Static variables to control exceptions
    never_end_during_setup = False  # type: bool
    never_end_during_execute = False  # type: bool
    never_end_during_cleanup = False  # type: bool

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step Pass"),
            TestStep("Test Step Sleep Infinitely Maybe"),
            TestStep("Test Step Pass"),
        ]

    async def setup(self) -> None:
        if self.never_end_during_setup:
            logger.info("Test Case setup sleeping forever.")
            while True:
                await asyncio.sleep(1)

    async def execute(self) -> None:
        self.next_step()
        if self.never_end_during_execute:
            logger.info("Test Case execute sleeping forever.")
            while True:
                await asyncio.sleep(1)
        self.next_step()

    async def cleanup(self) -> None:
        if self.never_end_during_cleanup:
            logger.info("Test Case cleanup sleeping forever.")
            while True:
                await asyncio.sleep(1)


class TCNeverEndingV2(TestCase):
    metadata = {
        "public_id": "TCNeverEndingV2",
        "version": "1.2.3",
        "title": "Test Case that can sleep forever V2",
        "description": "This is a second version for TCNeverEnding Test case. "
        "No new feature is added to this test case compared to TCNeverEnding."
        "The goal of this test case is add a second Test Case to the same "
        "Test Suite TestSuiteNeverEnding.",
    }

    # Static variables to control exceptions
    never_end_during_setup = False  # type: bool
    never_end_during_execute = False  # type: bool
    never_end_during_cleanup = False  # type: bool

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Test Step Pass"),
            TestStep("Test Step Sleep Infinitely Maybe"),
            TestStep("Test Step Pass"),
        ]

    async def setup(self) -> None:
        if self.never_end_during_setup:
            logger.info("Test Case setup sleeping forever.")
            while True:
                await asyncio.sleep(1)

    async def execute(self) -> None:
        self.next_step()
        if self.never_end_during_execute:
            logger.info("Test Case execute sleeping forever.")
            while True:
                await asyncio.sleep(1)
        self.next_step()

    async def cleanup(self) -> None:
        if self.never_end_during_cleanup:
            logger.info("Test Case cleanup sleeping forever.")
            while True:
                await asyncio.sleep(1)
