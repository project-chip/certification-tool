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
from app.user_prompt_support import (
    PromptRequest,
    TextInputPromptRequest,
    UserPromptSupport,
    UserResponseStatusEnum,
)


class PromptResponseError(Exception):
    pass


class TCTRTextInputUserPrompt(TestCase, UserPromptSupport):
    metadata = {
        "public_id": "TCTRTextInputUserPrompt",
        "version": "1.2.3",
        "title": "This is Test Case tctr_text_input_user_prompt",
        "description": """This Test Case is built to test the test runner,\
             step 2 is supposed to run for ever""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("No-op"),
            TestStep("Prompt User"),
            TestStep("Pass on option 1"),
        ]

    def _create_custom_prompt_request(self) -> PromptRequest:
        text_input_param = {
            "prompt": "Please type email info in the text box",
            "placeholder_text": "some@email.com",
            "default_value": "some@email.com",
            "regex_pattern": "^\\S+@\\S+\\.\\S+$",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=2,
        )
        return prompt_request

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        logger.info("This is a test step 1: No-op")
        self.next_step()

        logger.info("This is a test step 2: Prompting the user")

        prompt_request = self._create_custom_prompt_request()
        prompt_response = await self.send_prompt_request(prompt_request=prompt_request)
        if prompt_response is None:
            raise PromptResponseError("User response returned Null")

        logger.info("This is a test step 3: Got the response " + str(prompt_response))
        if (
            prompt_response.status_code != UserResponseStatusEnum.OKAY
            or type(prompt_response.response) is not str
        ):
            raise PromptResponseError(
                "Failed test step 3: Expected respond to be type(str)"
            )
        self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
