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
from typing import Optional

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep
from app.user_prompt_support import (
    PromptResponse,
    UploadFile,
    UploadFilePromptRequest,
    UserPromptSupport,
    UserResponseStatusEnum,
)


class TestError(Exception):
    pass


class TCTRUploadFileUserPrompt(TestCase, UserPromptSupport):
    metadata = {
        "public_id": "TCTRUploadFileUserPrompt",
        "version": "1.2.3",
        "title": "UploadFile User Prompt Unit Test",
        "description": """This Test Case triggers the upload file user prompt.""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("No-op"),
            TestStep("Prompt User to Upload a File."),
        ]

    def __create_custom_upload_file_prompt_request(self) -> UploadFilePromptRequest:
        prompt = "Please upload of file:"
        return UploadFilePromptRequest(
            prompt=prompt,
            timeout=10,
        )

    async def setup(self) -> None:
        logger.info("Upload file usr prompt test case setup.")

    async def execute(self) -> None:
        logger.info("This test step does nothing.")
        self.next_step()

        logger.info("This test step prompts the user to upload a file.")

        prompt_request = self.__create_custom_upload_file_prompt_request()
        prompt_response = await self.send_prompt_request(prompt_request=prompt_request)
        self.__evaluate_user_response_for_errors(prompt_response)

        self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")

    def handle_uploaded_file(self, file: UploadFile) -> None:
        """Handles all uploaded files during this test case's execution."""
        logger.info(f"Received uploaded file: {file.filename}!")

    def __evaluate_user_response_for_errors(
        self, prompt_response: Optional[PromptResponse]
    ) -> None:
        if prompt_response is None:
            raise TestError("User response returned Null.")

        if prompt_response.status_code == UserResponseStatusEnum.TIMEOUT:
            raise TestError("User prompt timed out.")

        if prompt_response.status_code == UserResponseStatusEnum.CANCELLED:
            self.mark_step_failure("User cancelled the prompt.")
