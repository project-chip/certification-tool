from app.models.test_enums import TestStateEnum
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep
from app.user_prompt_support import PromptRequest, TextInputPromptRequest

from ..onboarding_script_support import (
    PROMPT_TIMEOUT,
    InvalidManualPairingCode,
    PayloadParsingTestBaseClass,
)


class TCDD12(PayloadParsingTestBaseClass):
    metadata = {
        "public_id": "TC-DD-1.2",
        "version": "0.0.1",
        "title": "TC-DD-1.2",
        "description": """This test case verifies that the manual
        pairing code payload contains the necessary information to
        onboard the device onto the CHIP network.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.MANUAL_PC",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Step1: Verify the first digit of the pairing code"),
            TestStep(
                """Step2: If the pairing code is 11 digits/the VID_PID
                flag is not set, verify the encoded elements"""
            ),
            TestStep(
                """Step2.b: If the pairing code is 21 digits
                 the VID_PID flag is set, verify the encoded elements"""
            ),
            TestStep(
                """Step3: Verify the 'check digit' of the pairing
                 code (digit 11 or 21)"""
            ),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1
        prompt_request = self._create_manual_pairing_code_prompt()
        prompt_resp = await self.invoke_prompt_and_get_int_response(prompt_request)
        manual_pairing_code = str(prompt_resp)
        logger.info("User input : {}".format(manual_pairing_code))
        digits_length = len(manual_pairing_code)
        if digits_length == 11:
            await self.validate_pairing_code_with_len_11(manual_pairing_code)
        elif digits_length == 21:
            await self.validate_pairing_code_with_len_21(manual_pairing_code)
        else:
            raise InvalidManualPairingCode(
                f"invalid manual pairing code of len {digits_length}"
            )

    async def cleanup(self) -> None:
        logger.info("TC-DD-1.2 Cleanup")

    async def validate_pairing_code_with_len_11(self, manual_pairing_code: str) -> None:
        first_digit = int(manual_pairing_code[0])
        digits_two_six = int(manual_pairing_code[1:5])
        digits_seven_ten = int(manual_pairing_code[6:10])

        # Step 1
        if not (0 <= first_digit <= 3):
            self.mark_step_failure(
                """The first digit must be between 0 and 3 when
                manual pairing code length is 11: {}""".format(
                    str(first_digit)
                )
            )
        logger.info("Manual pairing code first digit is: {}".format((first_digit)))
        self.next_step()

        # Step 2
        if not (00000 <= digits_two_six <= 65535):
            self.mark_step_failure(
                "Digits 2 thought 6 are not with in valid range: {}".format(
                    digits_two_six
                )
            )
        if not (0000 <= digits_seven_ten <= 8191):
            self.mark_step_failure(
                "Digits 7 thought 10 are not with in valid range: {}".format(
                    digits_seven_ten
                )
            )
        logger.info("Digits 2 through 6: {}".format(digits_two_six))
        logger.info("Digits 7 through 10: {}".format(digits_seven_ten))
        self.next_step()
        self.current_test_step.state = TestStateEnum.NOT_APPLICABLE
        self.next_step()  # Skipping test step 2b as only applicable when len is 21

        # Step 3
        await self._validate_check_digit(manual_pairing_code, "10")

    async def validate_pairing_code_with_len_21(self, manual_pairing_code: str) -> None:
        first_digit = int(manual_pairing_code[0])
        digits_two_six = int(manual_pairing_code[1:5])
        digits_seven_ten = int(manual_pairing_code[6:10])
        digits_eleven_fifteen = int(manual_pairing_code[10:14])
        digits_sixteen_twenty = int(manual_pairing_code[15:20])

        # Step1
        if not (4 <= first_digit <= 7):
            self.mark_step_failure(
                """The first digit must be between 4 and 7 when
                manual pairing code length is 21: {}""".format(
                    str(first_digit)
                )
            )
        logger.info("Manual pairing code first digit is: {}".format((first_digit)))

        self.next_step()
        self.current_test_step.state = TestStateEnum.NOT_APPLICABLE
        self.next_step()  # Skipping test step 2 as only applicable when len is 11

        if not (00000 <= digits_two_six <= 65535):
            self.mark_step_failure(
                "Digits 2 thought 6 are not with in valid range: {}".format(
                    digits_two_six
                )
            )
        if not (0000 <= digits_seven_ten <= 8191):
            self.mark_step_failure(
                "Digits 7 thought 10 are not with in valid range: {}".format(
                    digits_seven_ten
                )
            )
        if not (0000 <= digits_eleven_fifteen <= 65535):
            self.mark_step_failure(
                "Digits 11 thought 15 are not with in valid range: {}".format(
                    digits_eleven_fifteen
                )
            )
        if not (0000 <= digits_sixteen_twenty <= 65535):
            self.mark_step_failure(
                "Digits 16 thought 20 are not with in valid range: {}".format(
                    digits_sixteen_twenty
                )
            )
        logger.info("Digits 2 through 6: {}".format(digits_two_six))
        logger.info("Digits 7 through 10: {}".format(digits_seven_ten))
        logger.info("Digits 11 through 15: {}".format(digits_eleven_fifteen))
        logger.info("Digits 16 through 20: {}".format(digits_sixteen_twenty))
        self.next_step()
        # Step 3
        await self._validate_check_digit(manual_pairing_code, "20")

    async def _validate_check_digit(
        self, manual_pairing_code: str, checksum_index: str
    ) -> None:
        checksum_check = await self.chip_tool_manual_pairing_code_checksum_check(
            manual_pairing_code, checksum_index
        )
        if checksum_check is False:
            self.mark_step_failure(
                "Validation failed for 'check digit' of the pairing code"
            )

    def _create_manual_pairing_code_prompt(self) -> PromptRequest:
        text_input_param = {
            "prompt": "Please enter the Manual pairing code",
            "placeholder_text": "34970112332",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=PROMPT_TIMEOUT,
        )
        return prompt_request
