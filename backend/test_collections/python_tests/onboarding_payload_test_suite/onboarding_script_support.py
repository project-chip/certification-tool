from app.chip_tool import ChipTool, ChipToolTestType
from app.chip_tool.chip_tool import CHIP_TOOL_EXE
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models.test_case import TestCase
from app.user_prompt_support import PromptRequest, TextInputPromptRequest
from app.user_prompt_support.user_prompt_support import UserPromptSupport

PROMPT_TIMEOUT = 60


class ParsedPayload:
    def __init__(
        self,
        version: int,
        rendezvousInfo: int,
        discriminator: int,
        setUpPINCode: int,
        vendorID: int,
        productID: int,
        commissioningFlow: int,
    ):
        self.version = version
        self.rendezvousInfo = rendezvousInfo
        self.discriminator = discriminator
        self.setUpPINCode = setUpPINCode
        self.vendorID = vendorID
        self.productID = productID
        self.commissioningFlow = commissioningFlow


class PayloadParsingError(Exception):
    pass


class InvalidManualPairingCode(Exception):
    pass


class PayloadParsingTestBaseClass(TestCase, UserPromptSupport, object):
    test_type = ChipToolTestType.CHIP_TOOL

    async def chip_tool_manual_pairing_code_checksum_check(
        self, pairing_code: str, checksum_index: str
    ) -> bool:
        chip_tool = ChipTool()
        await chip_tool.start_container(self.test_type)
        assert chip_tool.is_running()
        checksum_verify_command = "payload verhoeff-verify"
        result = chip_tool.send_command(
            f"{checksum_verify_command} {pairing_code} {checksum_index}",
            prefix=CHIP_TOOL_EXE,
        )
        logger.info(f"chip-tool output : {result}")
        if "INVALID" in result.output.decode("utf-8"):
            return False
        else:
            return True

    async def chip_tool_parse_onboarding_code(self, code_payload: str) -> ParsedPayload:
        chip_tool = ChipTool()
        await chip_tool.start_container(self.test_type)
        assert chip_tool.is_running()
        qr_code_parse_command = "payload parse-setup-payload"
        result = chip_tool.send_command(
            f"{qr_code_parse_command} {code_payload}", prefix=CHIP_TOOL_EXE
        )
        logger.info(f"chip-tool output : {result}")
        try:
            cmd_output = result.output.decode("utf-8").split("\n")
            parsed_attributes = {}
            parsed_payload = None
            for output_line in cmd_output:
                attribute_details = output_line.split(": ")
                if len(attribute_details) == 3:
                    parameter_value = attribute_details[2]
                    if "(" in parameter_value:
                        parameter_value = parameter_value.split("(")[0]
                    parsed_attributes[attribute_details[1]] = parameter_value
            if (
                "Version" not in parsed_attributes
                or "Discovery Bitmask" not in parsed_attributes
                or "Long discriminator" not in parsed_attributes
                or "Passcode" not in parsed_attributes
                or "VendorID" not in parsed_attributes
                or "ProductID" not in parsed_attributes
                or "Custom flow" not in parsed_attributes
            ):
                raise PayloadParsingError(
                    f"""Error parsing onboarding payload.
                    Missing required payload fields {parsed_attributes}"""
                )

            parsed_payload = ParsedPayload(
                int(parsed_attributes["Version"]),
                int(parsed_attributes["Discovery Bitmask"], 16),
                int(parsed_attributes["Long discriminator"]),
                int(parsed_attributes["Passcode"]),
                int(parsed_attributes["VendorID"]),
                int(parsed_attributes["ProductID"]),
                int(parsed_attributes["Custom flow"]),
            )
        except (AttributeError, UnicodeDecodeError) as error:
            raise PayloadParsingError(
                f"Error decoding onboarding payload. Error {error}"
            )
        chip_tool.destroy_device()
        return parsed_payload

    def create_onboarding_code_payload_prompt(self, code_type: str) -> PromptRequest:
        text_input_param = {
            "prompt": f"Please enter the {code_type} code payload",
            "placeholder_text": "MT:YNJV75HZ00KA0648G00",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=PROMPT_TIMEOUT,
        )
        return prompt_request

    def create_discriminator_prompt(self) -> PromptRequest:
        text_input_param = {
            "prompt": "Please enter 12-bit discriminator from the device advertisement",
            "placeholder_text": "0xF00",
        }
        prompt_request = TextInputPromptRequest(
            **text_input_param,
            timeout=PROMPT_TIMEOUT,
        )
        return prompt_request

    def payload_version_check(self, version: int) -> None:
        if version != 0x0:
            self.mark_step_failure(
                f"Invalid NFC code payload version, detected value: {version}"
            )
            return
        logger.info("Verified QR code payload version: {bin(version)}")

    def payload_rendezvous_capabilities_bit_mask_check(
        self, discovery_capabilities_bitmask: int
    ) -> None:
        if not (0 <= discovery_capabilities_bitmask <= 7):
            self.mark_step_failure(
                f"""Invalid rendezvous capabilities bit mask,
                detected value: {bin(discovery_capabilities_bitmask)}"""
            )
            return
        logger.info(
            f"""Verified rendezvous capabilities bit mask:
            {bin(discovery_capabilities_bitmask)}"""
        )

    async def payload_discriminator_check(self, discriminator: int) -> None:
        prompt_request = self.create_discriminator_prompt()
        prompt_response = await self.invoke_prompt_and_get_str_response(prompt_request)
        discriminator_in_advt_frame = int(prompt_response, 16)
        if discriminator != discriminator_in_advt_frame:
            self.mark_step_failure(
                f"""Discriminator does not matches the value advertized by
                 device during commissioning. Value in advertisement frame
                 {bin(discriminator_in_advt_frame)}, value in QR code payload
                 {bin(discriminator)}"""
            )
            return
        logger.info(f"Verified discriminator bit mask: {bin(discriminator)}")

    def payload_passcode_check(self, passcode: int) -> None:
        if not (0x1 <= passcode <= 0x5F5E0FE):
            self.mark_step_failure(f"Invalid passcode, detected value: {hex(passcode)}")
            return
        logger.info(f"Verified passcode is 27-bit: {hex(passcode)}")
        self.next_step()
        invalid_passcodes = [
            00000000,
            11111111,
            22222222,
            33333333,
            44444444,
            55555555,
            66666666,
            77777777,
            88888888,
            99999999,
            12345678,
            87654321,
        ]
        if (not (0x1 <= passcode <= 0x5F5E0FE)) and (passcode in invalid_passcodes):
            self.mark_step_failure(f"Invalid passcode, detected value: {hex(passcode)}")
            return
        logger.info(f"Verified passcode: {hex(passcode)}")

    def payload_prefix_check(self, code_prefix: str) -> None:
        if code_prefix != "MT:":
            self.mark_step_failure(
                f"Invalid onboarding code prefix, detected value: {code_prefix}"
            )
            return
        logger.info(f"Verified onboarding code prefix: {code_prefix}")

    def vendorid_productid_check(self, vendor_id: int, product_id: int) -> None:
        # Issue#30:Verify Vendor ID and Product ID against Distributed Compliance Ledger
        logger.info(
            f"""TODO: Verified Vendor ID and Product ID, VID:{vendor_id},
            PID:{product_id}"""
        )

    def custom_payload_support_check(self, commissioningFlow: int) -> None:
        if not (0x0 <= commissioningFlow <= 0x02):
            self.mark_step_failure(
                f"Invalid custom flow, detected value: {hex(commissioningFlow)}"
            )
            return
        logger.info(f"Verified custom flow value: {hex(commissioningFlow)}")
