from enum import IntEnum
from typing import Optional

from app.models import TestCaseExecution
from app.models.test_enums import TestStateEnum
from app.test_engine.logger import test_engine_logger as logger
from app.user_prompt_support import (
    OptionsSelectPromptRequest,
    PromptResponse,
    UploadFile,
    UploadFilePromptRequest,
    UserPromptSupport,
    UserResponseStatusEnum,
)

from .test_case import TestCase
from .test_step import TestStep

OUTCOME_TIMEOUT_S = 60 * 10  # Seconds
LOG_UPLOAD_TIMEOUT_S = 60 * 10  # Seconds


class TestError(Exception):
    """Raised when an error occurs during execution."""


class PromptOptions(IntEnum):
    PASS = 1
    FAIL = 2
    NOT_APPLICABLE = 3


class ManualVerificationTestStep(TestStep, UserPromptSupport):
    """Test Step used to generate manual test steps with verification text"""

    def __init__(self, name: str, verification: Optional[str] = None) -> None:
        super().__init__(name=name)
        self.verification = verification

    async def prompt_verification_step(self) -> bool:
        """Sends a prompt request to present instructions and get outcome from user.

        Raises:
            ValueError: When receiving an unexpected response

        Returns:
            bool: False if user responds Failed
        """
        prompt = self.name
        if self.verification is not None:
            prompt += f"\n\n{self.verification}"

        options = {
            "PASS": PromptOptions.PASS,
            "FAIL": PromptOptions.FAIL,
            "NOT APPLICABLE": PromptOptions.NOT_APPLICABLE,
        }
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=OUTCOME_TIMEOUT_S
        )
        prompt_response = await self.send_prompt_request(prompt_request)
        self.__evaluate_user_response_for_errors(prompt_response)

        if prompt_response.response == PromptOptions.FAIL:
            self.append_failure("User stated manual step FAILED.")
            return False
        elif prompt_response.response == PromptOptions.PASS:
            logger.info("User stated this manual step PASSED.")
            return True
        elif prompt_response.response == PromptOptions.NOT_APPLICABLE:
            self.mark_as_not_applicable(
                "User stated this manual step is \
            NOT APPLICABLE."
            )
            return True
        else:
            raise ValueError(
                f"Received unknown prompt option: {prompt_response.response}"
            )

    def __evaluate_user_response_for_errors(
        self, prompt_response: Optional[PromptResponse]
    ) -> None:
        if prompt_response is None:
            raise TestError("User response returned Null.")

        if prompt_response.response is None:
            raise ValueError("No response received for manual test case outcome.")

        if prompt_response.status_code == UserResponseStatusEnum.TIMEOUT:
            raise TestError("User prompt timed out.")

        if prompt_response.status_code == UserResponseStatusEnum.CANCELLED:
            self.append_failure("User cancelled the prompt.")


class ManualLogUploadStep(TestStep, UserPromptSupport):
    async def send_prompt_to_upload_log(self) -> None:
        """Sends a prompt request to get an evidence log uploaded from the user."""
        prompt_title = (
            f"Upload a manually generated log file for {self.test_case_id()}. "
            + "Allowed types: .txt, .log"
        )
        prompt_request = UploadFilePromptRequest(
            prompt=prompt_title,
            timeout=OUTCOME_TIMEOUT_S,
        )
        prompt_response = await self.send_prompt_request(prompt_request)

        if prompt_response is None:
            raise TestError("User response returned Null.")

        if prompt_response.status_code == UserResponseStatusEnum.TIMEOUT:
            raise TestError("User prompt timed out.")

        if prompt_response.status_code == UserResponseStatusEnum.CANCELLED:
            self.append_failure("User cancelled log upload prompt.")

    def test_case_id(self) -> str:
        if self.test_step_execution:
            return self.test_step_execution.test_case_execution.public_id
        else:
            # Unlikely to occur. Must handle the optional `test_step_execution`.
            return "Unknown"

    def handle_uploaded_file(self, file: UploadFile) -> None:
        """Handles all uploaded files during this test case's execution."""
        # Fail the log upload step if the log file is not in text format
        allowed_content_types = {"text/plain", "application/octet-stream"}
        if file.content_type not in allowed_content_types:
            self.append_failure(
                f"Unsupported log file format: {file.content_type}. "
                + "Only text format (.log, .txt) log files can be uploaded.",
            )
            return

        logger.info(f"Uploading manual log: {file.filename}")
        logger.info("---- Start of Manual Log ----")
        with file.file as f:
            for line in f:
                logger.info(line.decode("utf-8").strip())
        logger.info("---- End of Manual Log ----")


class ManualTestCase(TestCase, UserPromptSupport):
    """Test case used to generate all manual test cases.

    ManualTestCases will only display the name of each step and
    always end execution by asking the user:
        1) If the device PASSED or FAILED the manual case.
        2) If PASSED: To upload a manually generated chip-tool log
           demonstrating that the device PASSED.

    The create_test_steps() method must still be overwritten by subclasses.
    """

    def __init__(self, test_case_execution: TestCaseExecution) -> None:
        super().__init__(test_case_execution=test_case_execution)
        self.__inject_prompt_steps()

    async def setup(self) -> None:
        logger.info("-------- Start of MANUAL Test Case --------")
        logger.info("Please complete the following steps of this test case manually:")

    async def execute(self) -> None:
        # The last step is to prompt for log upload (injected for all manual tests).
        # This step will be handled separately, outside the for loop.
        for i in range(len(self.test_steps[:-1])):
            step = self.current_test_step
            logger.info(f"Step {i}: {step.name}.")
            if isinstance(step, ManualVerificationTestStep):
                await step.prompt_verification_step()
            else:
                logger.error(f"Unsupported test test {step.__class__}")
            self.next_step()

        if isinstance(self.current_test_step, ManualLogUploadStep):
            # Do not prompt for log upload if all test steps have been skipped
            if self.__skipped_all_manual_test_steps():
                self.current_test_step.state = TestStateEnum.NOT_APPLICABLE
            else:
                await self.current_test_step.send_prompt_to_upload_log()

    async def cleanup(self) -> None:
        logger.info("-------- End of MANUAL Test Case --------")

    def handle_uploaded_file(self, file: UploadFile) -> None:
        if isinstance(self.current_test_step, ManualLogUploadStep):
            self.current_test_step.handle_uploaded_file(file)
        else:
            raise TestError("Unexpected log upload")

    def __inject_prompt_steps(self) -> None:
        """Add steps to prompt user to upload a log."""
        self.test_steps.append(ManualLogUploadStep("Prompt Manual Log Upload"))

    def __skipped_all_manual_test_steps(self) -> bool:
        """Returns True if all manual test steps have been skipped"""
        # The log upload step (last step) cannot be skipped
        for step in self.test_steps[:-1]:
            if step.state != TestStateEnum.NOT_APPLICABLE:
                return False

        return True
