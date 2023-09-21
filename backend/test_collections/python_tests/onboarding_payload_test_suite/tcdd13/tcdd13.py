from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep

from ..onboarding_script_support import PayloadParsingTestBaseClass


class TCDD13(PayloadParsingTestBaseClass):
    metadata = {
        "public_id": "TC-DD-1.3",
        "version": "0.0.1",
        "title": "TC-DD-1.3",
        "description": """This test case verifies
         that the onboarding NFC code contains the
         necessary information to onboard the
         device onto the CHIP network.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.NFC",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep(
                "Step1: Power up the DUT and put the DUT in pairing mode\
                     and bring the NFC code reader close to the DUT"
            ),
            TestStep("Step3.a: Verify the NFC code payload version"),
            TestStep("Step3.b: Verify 8-bit Rendezvous Capabilities bit mask"),
            TestStep("Step3.c: Verify the 12-bit discriminator bit mask"),
            TestStep(
                "Step3.d: Verify the onboarding payload contains a 27-bit Passcode"
            ),
            TestStep("Step3.e: Verify passcode is valid"),
            TestStep("Step3.f: Verify NFC code prefix"),
            TestStep("Step3.g: Verify Vendor ID and Product ID"),
            TestStep("Step5: Verify Custom payload support"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1 and 2
        # Fetch NFC code payload from UI/NFC code reader.
        prompt_request = self.create_onboarding_code_payload_prompt("NFC")
        prompt_response = await self.invoke_prompt_and_get_str_response(prompt_request)
        logger.info(f"User input : {prompt_response}")
        nfc_code_payload = await self.chip_tool_parse_onboarding_code(prompt_response)
        logger.info(f"parsed payload : {nfc_code_payload}")
        self.next_step()
        # Test step 3.a
        self.payload_version_check(nfc_code_payload.version)
        self.next_step()
        # Test step 3.b
        self.payload_rendezvous_capabilities_bit_mask_check(
            nfc_code_payload.rendezvousInfo
        )
        self.next_step()
        # Test step 3.c
        # TODO Extract discriminator from device advertises frame Issue#186
        await self.payload_discriminator_check(nfc_code_payload.discriminator)
        self.next_step()
        # Test step 3.d
        self.payload_passcode_check(nfc_code_payload.setUpPINCode)
        self.next_step()
        # Test step 3.f
        nfc_code_prefix = prompt_response[:3]
        self.payload_prefix_check(nfc_code_prefix)
        self.next_step()
        # Test step 3.g
        self.vendorid_productid_check(
            nfc_code_payload.vendorID, nfc_code_payload.productID
        )
        self.next_step()
        # Test step 5
        self.custom_payload_support_check(nfc_code_payload.commissioningFlow)

    async def cleanup(self) -> None:
        logger.info("TC-DD-1.3 Cleanup")
