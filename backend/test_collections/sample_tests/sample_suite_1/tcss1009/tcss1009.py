import random
from enum import IntEnum
from typing import Optional

from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep
from app.user_prompt_support import (
    OptionsSelectPromptRequest,
    PromptResponse,
    UserPromptSupport,
    UserResponseStatusEnum,
)


class TestError(Exception):
    pass


class PromptOptions(IntEnum):
    YES_FAIL = 1
    NO_PASS = 2
    RANDOM = 3


class TCSS1009(TestCase, UserPromptSupport):
    metadata = {
        "public_id": "TCSS1009",
        "version": "1.2.3",
        "title": "User prompt sample test",
        "description": """This is Test Case tcss1009,\
        it will not get a very long description""",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Always pass"),
            TestStep("Prompt user"),
            TestStep("Evaluate user response"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Step 1:
        self.next_step()

        # Step 2:
        prompt_response = await self.__prompt_user()
        self.next_step()

        # Step 3:
        self.__evaluate_user_response(prompt_response)

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")

    async def __prompt_user(self) -> Optional[PromptResponse]:
        prompt = "Do you want this test to fail?"
        options = {
            "Yes, please": PromptOptions.YES_FAIL,
            "No, please pass it": PromptOptions.NO_PASS,
            "Make it random": PromptOptions.RANDOM,
        }
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=30
        )
        return await self.send_prompt_request(prompt_request)

    def __evaluate_user_response(
        self, prompt_response: Optional[PromptResponse]
    ) -> None:
        if prompt_response is None:
            raise TestError("User response returned Null")

        if prompt_response.status_code == UserResponseStatusEnum.TIMEOUT:
            raise TestError("User prompt timed out")

        if prompt_response.status_code == UserResponseStatusEnum.CANCELLED:
            self.mark_step_failure("User cancelled the prompt")
            return

        if prompt_response.status_code == UserResponseStatusEnum.INVALID:
            self.mark_step_failure("User prompt response is invalid")
            return

        if prompt_response.response == PromptOptions.YES_FAIL:
            self.mark_step_failure("User wanted test to fail")
            return

        if prompt_response.response == PromptOptions.NO_PASS:
            return

        if prompt_response.response == PromptOptions.RANDOM:
            # Answer: Make it random
            if bool(random.getrandbits(1)):
                self.mark_step_failure("Test randomly failed")
