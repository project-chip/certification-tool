from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep

from ..onboarding_script_support import PayloadParsingTestBaseClass


class TCDD11(PayloadParsingTestBaseClass):
    metadata = {
        "public_id": "TC-DD-1.1",
        "version": "0.0.1",
        "title": "TC-DD-1.1",
        "description": """This test case verifies that the
        onboarding QR code payload contains the necessary 
        information to onboard the device onto the CHIP network.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.QR",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Step1: Scan the DUT’s QR code using a QR code reader"),
            TestStep("Step2.a: Verify the QR code payload version"),
            TestStep("Step2.b: Verify 8-bit Rendezvous Capabilities bit mask"),
            TestStep("Step2.c: Verify the 12-bit discriminator bit mask"),
            TestStep(
                "Step2.d: Verify the onboarding payload contains a 27-bit Passcode"
            ),
            TestStep("Step2.e: Verify passcode is valid"),
            TestStep("Step2.f: Verify QR code prefix"),
            TestStep("Step2.g: Verify Vendor ID and Product ID"),
            TestStep("Step4: Verify Custom payload support"),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1
        # Fetch QR code payload from UI/QR code reader.
        prompt_request = self.create_onboarding_code_payload_prompt("QR")
        prompt_response = await self.invoke_prompt_and_get_str_response(prompt_request)
        logger.info(f"User input : {prompt_response}")
        qr_code_payload = await self.chip_tool_parse_onboarding_code(prompt_response)
        logger.info(f"parsed payload : {qr_code_payload}")
        self.next_step()
        # Test step 2.a
        self.payload_version_check(qr_code_payload.version)
        self.next_step()
        # Test step 2.b
        self.payload_rendezvous_capabilities_bit_mask_check(
            qr_code_payload.rendezvousInfo
        )
        self.next_step()
        # Test step 2.c
        # TODO Extract discriminator from device advertises frame Issue#186
        await self.payload_discriminator_check(qr_code_payload.discriminator)
        self.next_step()
        # Test step 2.d
        self.payload_passcode_check(qr_code_payload.setUpPINCode)
        self.next_step()
        # Test step 2.f
        qr_code_prefix = prompt_response[:3]
        self.payload_prefix_check(qr_code_prefix)
        self.next_step()
        # Test step 2.g
        self.vendorid_productid_check(
            qr_code_payload.vendorID, qr_code_payload.productID
        )
        self.next_step()
        # Test step 4
        self.custom_payload_support_check(qr_code_payload.commissioningFlow)

    async def cleanup(self) -> None:
        logger.info("TC-DD-1.1 Cleanup")
