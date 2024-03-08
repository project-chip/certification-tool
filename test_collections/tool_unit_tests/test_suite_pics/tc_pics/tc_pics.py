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
from app.test_engine.models import TestCase, TestStep


class TCPics(TestCase):
    metadata = {
        "public_id": "TC_Pics",
        "version": "1.2.3",
        "title": "TC_Pics (Test)",
        "description": "Test PICS test case for unit testing",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "AB.C",
                "AB.C.A0004",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [TestStep("Test Step 1")]
        self.test_steps = [TestStep("Test Step 2")]
        self.test_steps = [TestStep("Test Step 3")]
