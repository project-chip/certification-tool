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
"""Manual Test Case Unit Test."""

from app.test_engine.models import ManualTestCase, TestStep


class TCManual(ManualTestCase):
    metadata = {
        "public_id": "TCManual",
        "version": "1.2.3",
        "title": "A Test Case that must be done manually.",
        "description": "This Test case will prompt the user if this case"
        "pass/failed and to upload a log as evidence.",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Manually preform this step first."),
            TestStep("Manually perform this step second."),
            TestStep("Manually perform this step last."),
        ]
