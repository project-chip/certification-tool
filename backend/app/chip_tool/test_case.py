import asyncio
from enum import Enum, IntEnum
from typing import Any

# Websocket Test imports:
from matter_chip_tool_adapter.decoder import MatterLog
from matter_yamltests.hooks import TestRunnerHooks
from matter_yamltests.parser import PostProcessResponseResult, TestStep

from app.chip_tool import ChipTool
from app.chip_tool.chip_tool import ChipToolTestType
from app.models import TestStateEnum
from app.models.test_case_execution import TestCaseExecution
from app.test_engine.logger import CHIP_LOG_FORMAT, CHIPTOOL_LEVEL, test_engine_logger
from app.test_engine.models import TestCase
from app.test_engine.models.manual_test_case import (
    ManualLogUploadStep,
    ManualVerificationTestStep,
)
from app.user_prompt_support import OptionsSelectPromptRequest
from app.user_prompt_support.uploaded_file_support import UploadFile
from app.user_prompt_support.user_prompt_manager import user_prompt_manager
from app.user_prompt_support.user_prompt_support import UserPromptSupport

CHIP_TOOL_DEFAULT_PROMPT_TIMEOUT_S = 60  # seconds
OUTCOME_TIMEOUT_S = 60 * 10  # Seconds


class ChipToolPromptTypeEnum(str, Enum):
    CHIP_APP_WAIT_FOR_PROMPT = "Wait for"
    CHIP_APP_QUERY_PROMPT = "Query"
    CHIP_APP_USER_PROMPT = "USER_PROMPT"


class PromptOption(IntEnum):
    PASS = 1
    FAIL = 2
    NOT_APPLICABLE = 3
    RETRY = 4
    CANCEL = 5


class TestError(Exception):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"


class ChipToolTest(TestCase, UserPromptSupport, TestRunnerHooks):
    chip_tool: ChipTool
    chip_tool_test_identifier: str
    test_type: ChipToolTestType

    def __init__(self, test_case_execution: TestCaseExecution):
        self.__show_adapter_logs = False
        self.__show_adapter_logs_on_error = False
        self.__index = 1
        self.__successes = 0
        self.__warnings = 0
        self.__errors = 0
        self.__runned = 0
        self.__skipped = 0
        self.__current_prompt = None
        super(ChipToolTest, self).__init__(test_case_execution)

    def start(self, count: int) -> None:
        return

    def stop(self, duration: int) -> None:
        pass

    def test_start(self, filename: str, name: str, count: int) -> None:
        # This is necessary in order to synchronize model and runner steps
        # since there is step execute outside runner context
        self.next_step()

    def test_stop(self, duration: int) -> None:
        self.current_test_step.mark_as_completed()

    def step_skipped(self, name: str, expression: str) -> None:
        if user_prompt_manager.current_prompt_exchange:
            user_prompt_manager.select_prompt_option(
                user_prompt_manager.current_prompt_exchange, PromptOption.NOT_APPLICABLE
            )
        self.current_test_step.mark_as_not_applicable(
            f"Test step skipped: {name}. {expression} == False"
        )
        self.__index += 1
        self.__skipped += 1
        self.next_step()

    def step_start(self, request: TestStep) -> None:
        if (
            self.test_type == ChipToolTestType.CHIP_APP
            and
            # Manual steps will be handled by step_manual function.
            not isinstance(self.current_test_step, ManualVerificationTestStep)
        ):
            prompt = f"{request.label}"
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(
                self.__prompt_user_for_controller_action(prompt), loop=loop
            )
        self.__index += 1

    def step_unknown(self) -> None:
        self.__runned += 1

    async def step_manual(self) -> None:
        step = self.current_test_step
        if not isinstance(step, ManualVerificationTestStep):
            raise TestError(f"Unexpected user prompt found in test step: {step.name}")

        try:
            await asyncio.wait_for(
                self.__prompt_user_manual_step(step), OUTCOME_TIMEOUT_S
            )
        except asyncio.TimeoutError:
            self.current_test_step.append_failure("Prompt timed out.")
        self.next_step()

    async def __prompt_user_manual_step(self, step: ManualVerificationTestStep) -> None:
        result = await step.prompt_verification_step()

        if not result:
            self.current_test_step.append_failure("Manual Test Step Failure.")

    def step_success(
        self, logger: Any, logs: Any, duration: int, request: TestStep
    ) -> None:
        self.__handle_logs(logs)

        if user_prompt_manager.current_prompt_exchange:
            user_prompt_manager.select_prompt_option(
                user_prompt_manager.current_prompt_exchange, PromptOption.PASS
            )

        self.next_step()

    def step_failure(
        self, logger: Any, logs: Any, duration: int, request: TestStep, received: Any
    ) -> None:
        self.__handle_logs(logs)

        if user_prompt_manager.current_prompt_exchange:
            user_prompt_manager.select_prompt_option(
                user_prompt_manager.current_prompt_exchange, PromptOption.FAIL
            )

        self.__report_failures(logger, request, received)

        self.next_step()

    def __report_failures(self, logger: Any, request: TestStep, received: Any) -> None:
        """
        The logger from runner contains all logs entries for the test step, this method
        seeks for the error entries.
        """
        if not logger or not isinstance(logger, PostProcessResponseResult):
            # It is expected the runner to return a PostProcessResponseResult,
            # but in case of returning a different type
            self.current_test_step.append_failure(
                "Test Step Failure: \n "
                f"Expected: {request.responses} \n Received: {received}"
            )
            return

        # Iterate through the entries seeking for the errors entries
        for log_entry in logger.entries:
            if log_entry.is_error():
                # Check if the step error came from exception or not, since the message
                # in exception object has more details
                # TODO: There is an issue raised in SDK runner in order to improve the
                # message from log_entry:
                # https://github.com/project-chip/connectedhomeip/issues/28101
                if log_entry.exception:
                    self.current_test_step.append_failure(log_entry.exception.message)
                else:
                    self.current_test_step.append_failure(log_entry.message)

    async def setup(self) -> None:
        if (
            self.chip_tool_test_identifier is None
            or len(self.chip_tool_test_identifier) == 0
        ):
            raise TestError(
                "Invalid chip-tool test identifier: "
                f"'{self.chip_tool_test_identifier}'. Expected non-empty string."
            )

        self.chip_tool = ChipTool()

        # Use test engine logger to log all events to test run.
        self.chip_tool.logger = test_engine_logger
        if not self.chip_tool.is_running():
            raise TestError("Unable to execute test as chip-tool is not available")

    async def execute(self) -> None:
        test_name = f"Test_{self.chip_tool_test_identifier}"
        await self.chip_tool.run_test(
            test_step_interface=self,
            test_id=test_name,
            test_type=self.test_type,
            test_parameters=self.test_parameters,
        )

    async def cleanup(self) -> None:
        pass

    async def __prompt_user_for_controller_action(self, action: str) -> None:
        """Prompt the user for the controller action string

        Args:
            action (str): The action string the TH is waiting for

        Raises:
            TestError: When response is null
            TestError: Response is unexpected
        """

        options = {
            "PASS": PromptOption.PASS,
            "FAIL": PromptOption.FAIL,
            "NOT APPLICABLE": PromptOption.NOT_APPLICABLE,
        }
        prompt = f"Please do the following action on the Controller: {action}"
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=60
        )
        await self.send_prompt_request(prompt_request)

    def __handle_logs(self, logs: Any) -> None:
        for log_entry in logs:
            if not isinstance(log_entry, MatterLog):
                continue

            test_engine_logger.log(
                CHIPTOOL_LEVEL,
                CHIP_LOG_FORMAT.format(log_entry.module, log_entry.message),
            )


class ChipToolManualPromptTest(ChipToolTest):
    def __init__(self, test_case_execution: TestCaseExecution) -> None:
        super().__init__(test_case_execution=test_case_execution)
        self.__inject_log_prompt_step()

    async def execute(self) -> None:
        await super().execute()
        self.next_step()

        if isinstance(self.current_test_step, ManualLogUploadStep):
            # Do not prompt for log upload if all manual test steps have been skipped
            if self.__skipped_all_manual_test_steps():
                self.current_test_step.state = TestStateEnum.NOT_APPLICABLE
            else:
                await self.current_test_step.send_prompt_to_upload_log()

    def handle_uploaded_file(self, file: UploadFile) -> None:
        if isinstance(self.current_test_step, ManualLogUploadStep):
            self.current_test_step.handle_uploaded_file(file)
        else:
            raise TestError("Unexpected log upload")

    def __inject_log_prompt_step(self) -> None:
        """Add step to prompt user to upload a log."""
        self.test_steps.append(ManualLogUploadStep("Prompt Manual Log Upload"))

    def __skipped_all_manual_test_steps(self) -> bool:
        """Returns True if all manual test steps have been skipped"""
        manual_test_steps = [
            step
            for step in self.test_steps
            if isinstance(step, ManualVerificationTestStep)
        ]

        for step in manual_test_steps:
            if step.state != TestStateEnum.NOT_APPLICABLE:
                return False

        return True
