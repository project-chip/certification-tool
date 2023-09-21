from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestCase, TestStep
from app.user_prompt_support import (
    PromptRequest,
    TextInputPromptRequest,
    UserPromptSupport,
)


class TCDD14(TestCase, UserPromptSupport):
    metadata = {
        "public_id": "TC-DD-1.4",
        "version": "0.0.1",
        "title": "TC-DD-1.4",
        "description": """This test case verifies that the
         onboarding QR code payload contain information on the
         onboarding of multiple DUT.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.CONCATENATED_QR_CODE",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep(
                "Step1: Scan the DUT’s QR code using a QR code\
                 reader and verify the number of delimiters."
            ),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1
        # Fetch QR code payload from UI/QR code reader.
        prompt_request = self._create_qr_code_payload_prompt()
        qr_code_payload_resp = await self.invoke_prompt_and_get_str_response(
            prompt_request
        )
        logger.info(f"User input : {qr_code_payload_resp}")
        prompt_request = self._create_dut_count_prompt()
        device_count_resp = await self.invoke_prompt_and_get_str_response(
            prompt_request
        )
        logger.info(f"User input : {device_count_resp}")
        onboarding_payload_delimiter_count = str(qr_code_payload_resp).count(
            "*"
        )  # Specification section "5.1.5. Concatenation" defines the '*' delimiter
        device_count = int(str(device_count_resp), 16)
        if onboarding_payload_delimiter_count != device_count - 1:
            self.mark_step_failure(
                f"""Invalid number of delimiters detected in QR code payload :
                {onboarding_payload_delimiter_count},
                expected {str(device_count - 1)}"""
            )

    async def cleanup(self) -> None:
        logger.info("TC-DD-1.4 Cleanup")

    def _create_qr_code_payload_prompt(self) -> PromptRequest:
        text_input_param = {
            "prompt": "Please enter the concatenated QR code payload",
            "placeholder_text": "MT:YNJV75HZ00KA0648G00*W0GU2OTB00KA0648G00",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=60,
        )
        return prompt_request

    def _create_dut_count_prompt(self) -> PromptRequest:
        text_input_param = {
            "prompt": "Please specify the number of devices that will be on-boarded.",
            "placeholder_text": "0x2",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=60,
        )
        return prompt_request
