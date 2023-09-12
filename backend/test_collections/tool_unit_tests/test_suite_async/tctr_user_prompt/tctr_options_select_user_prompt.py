from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep
from app.user_prompt_support import (
    OptionsSelectPromptRequest,
    PromptRequest,
    UserPromptSupport,
    UserResponseStatusEnum,
)


class TestError(Exception):
    pass


class TCTROptionsSelectUserPrompt(TestCase, UserPromptSupport):
    metadata = {
        "public_id": "TCTROptionsSelectUserPrompt",
        "version": "1.2.3",
        "title": "This is Test Case tctr_options_select_user_prompt",
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
        prompt = "Please select one of the following options"
        options = {"Options 1": 1, "Options 2": 2, "Options 3": 3, "Options 4": 4}
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=2
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
            raise TestError("User response returned Null")

        logger.info("This is a test step 3: Got the response " + str(prompt_response))
        if (
            prompt_response.status_code != UserResponseStatusEnum.OKAY
            or prompt_response.response != 1
        ):
            raise TestError("Failed test step 3: Expected Option 1")
        self.next_step()

    async def cleanup(self) -> None:
        logger.info("This is a test case cleanup")
