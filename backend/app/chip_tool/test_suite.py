from typing import Optional

from app.chip_tool import ChipTool
from app.chip_tool.chip_tool import ChipToolTestType
from app.chip_tool.test_case import PromptOption
from app.models import TestSuiteExecution
from app.otbr_manager.otbr_manager import ThreadBorderRouter
from app.schemas.test_environment_config import (
    DutPairingModeEnum,
    ThreadAutoConfig,
    ThreadExternalConfig,
)
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite
from app.user_prompt_support.prompt_request import OptionsSelectPromptRequest
from app.user_prompt_support.user_prompt_support import UserPromptSupport

CHIP_APP_PAIRING_CODE = "CHIP:SVR: Manual pairing code:"


class SuiteSetupError(Exception):
    pass


class DUTCommissioningError(Exception):
    pass


class ChipToolSuite(TestSuite, UserPromptSupport):
    chip_tool = ChipTool()
    border_router: Optional[ThreadBorderRouter] = None
    test_type: ChipToolTestType = ChipToolTestType.CHIP_TOOL
    __dut_commissioned_successfully: bool = False

    def __init__(self, test_suite_execution: TestSuiteExecution):
        super().__init__(test_suite_execution)

    async def setup(self) -> None:
        logger.info("Setting up chip_tool")
        # Use test engine logger to log all events to test run.
        self.chip_tool.logger = logger
        await self.chip_tool.start_container(
            self.test_type, self.config.dut_config.chip_tool_use_paa_certs
        )

        if len(self.pics.clusters) > 0:
            logger.info("Create PICS file for DUT")
            self.chip_tool.set_pics(pics=self.pics)
        else:
            # Disable sending "-PICS" option when running chip-tool
            self.chip_tool.reset_pics_state()

        if self.test_type == ChipToolTestType.CHIP_TOOL:
            logger.info("Commission DUT")
            await self.__commission_dut_allowing_retries()
        elif self.test_type == ChipToolTestType.CHIP_APP:
            logger.info("Verify Test suite prerequisites")
            await self.__verify_test_suite_prerequisites()

    async def __commission_dut_allowing_retries(self) -> None:
        """Try to commission DUT. If it fails, prompt user if they want to retry. Keep
        trying until commissioning succeeds or user chooses to cancel.

        Raises:
            SuiteSetupError: Commissioning failed and user chose not to retry
        """
        self.__dut_commissioned_successfully = False

        while not self.__dut_commissioned_successfully:
            try:
                await self.__pair_with_dut()
                self.__dut_commissioned_successfully = True
            except DUTCommissioningError as e:
                await self.__prompt_for_commissioning_retry(e)

    async def __pair_with_dut(self) -> None:
        if self.config.dut_config.pairing_mode is DutPairingModeEnum.ON_NETWORK:
            pair_result = await self.__pair_with_dut_onnetwork()
        elif self.config.dut_config.pairing_mode is DutPairingModeEnum.BLE_WIFI:
            pair_result = await self.__pair_with_dut_ble_wifi()
        elif self.config.dut_config.pairing_mode is DutPairingModeEnum.BLE_THREAD:
            pair_result = await self.__pair_with_dut_ble_thread()
        else:
            raise DUTCommissioningError("Unsupported DUT pairing mode")

        if not pair_result:
            raise DUTCommissioningError("Failed to pair with DUT")

    async def __pair_with_dut_onnetwork(self) -> bool:
        return await self.chip_tool.pairing_on_network(
            setup_code=self.config.dut_config.setup_code,
            discriminator=self.config.dut_config.discriminator,
        )

    async def __pair_with_dut_ble_wifi(self) -> bool:
        if self.config.network.wifi is None:
            raise DUTCommissioningError("Tool config is missing wifi config.")

        return await self.chip_tool.pairing_ble_wifi(
            ssid=self.config.network.wifi.ssid,
            password=self.config.network.wifi.password,
            setup_code=self.config.dut_config.setup_code,
            discriminator=self.config.dut_config.discriminator,
        )

    async def __pair_with_dut_ble_thread(self) -> bool:
        if self.config.network.thread is None:
            raise DUTCommissioningError("Tool config is missing thread config.")

        # if thread has ThreadAutoConfig, bring up border router
        thread_config = self.config.network.thread
        if isinstance(thread_config, ThreadExternalConfig):
            hex_dataset = thread_config.operational_dataset_hex
        elif isinstance(thread_config, ThreadAutoConfig):
            border_router = await self.__start_border_router(thread_config)
            hex_dataset = border_router.active_dataset
        else:
            raise DUTCommissioningError("Invalid thread configuration")

        return await self.chip_tool.pairing_ble_thread(
            hex_dataset=hex_dataset,
            setup_code=self.config.dut_config.setup_code,
            discriminator=self.config.dut_config.discriminator,
        )

    async def __start_border_router(
        self, config: ThreadAutoConfig
    ) -> ThreadBorderRouter:
        border_router = ThreadBorderRouter()
        if await border_router.start_device(config):
            await border_router.form_thread_topology()
        else:
            # This is unexpected but should work
            logger.warning("Reusing already running Border Router")

        self.border_router = border_router

        return border_router

    async def cleanup(self) -> None:
        # Unpair is not applicable for simulated apps case
        # Only unpair if commissioning was successfull during setup
        if (
            self.test_type == ChipToolTestType.CHIP_TOOL
            and self.__dut_commissioned_successfully
        ):
            logger.info("Unpairing chip_tool from device")
            await self.chip_tool.unpair()
        # Need a better way to trigger unpair for chip-app.
        elif self.test_type == ChipToolTestType.CHIP_APP:
            logger.info("Prompt user to perform decommissioning")
            await self.__prompt_user_to_perform_decommission()

        logger.info("Stopping chip-tool container")
        self.chip_tool.destroy_device()
        if self.border_router is not None:
            logger.info("Stopping border router container")
            self.border_router.destroy_device()

    async def __verify_test_suite_prerequisites(self) -> None:
        # prerequisites apply for CHIP_APP only.
        if self.test_type == ChipToolTestType.CHIP_APP:
            logger.info("Prompt user to perform commissioning")
            await self.__prompt_user_to_perform_commission()

    async def __prompt_for_commissioning_retry(
        self, error: DUTCommissioningError
    ) -> None:
        """Prompt the user if the commissioning should be retried

        Args:
            error (DUTCommissioningError): the commissioning error

        Raises:
            SuiteSetupError: Prompt response is CANCEL
            ValueError: Prompt response is unexpected
        """

        options = {
            "RETRY": PromptOption.RETRY,
            "CANCEL": PromptOption.CANCEL,
        }
        prompt = (
            f"Commissioning failed with error: {error}.\nIf you want to retry, please "
            "make sure that DUT is ready for commissioning and then select the "
            "'RETRY' option."
        )
        prompt_request = OptionsSelectPromptRequest(prompt=prompt, options=options)
        prompt_response = await self.send_prompt_request(prompt_request)

        match prompt_response.response:
            case PromptOption.RETRY:
                logger.info("User chose to RETRY commissioning")

            case PromptOption.CANCEL:
                raise SuiteSetupError(
                    "Failed to commission DUT and user chose not to retry"
                )

            case _:
                raise ValueError(
                    f"Received unknown prompt option for \
                        commissioning step: {prompt_response.response}"
                )

    async def __prompt_user_to_perform_commission(self) -> None:
        """Prompt the user to perform commissioning

        Raises:
            ValueError: Response is pairing failed or unexpected
        """

        options = {
            "Pairing successful": PromptOption.PASS,
            "Pairing Failed": PromptOption.FAIL,
        }
        prompt = """Please commission with the device using a controller:
                Example:
                    <Controller> pairing code <nodeid> <pairing code>
                """
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=60
        )
        prompt_response = await self.send_prompt_request(prompt_request)

        match prompt_response.response:
            case PromptOption.FAIL:
                raise ValueError("User stated commissioning step FAILED.")

            case PromptOption.PASS:
                logger.info("User stated commissioning step PASSED.")

            case _:
                raise ValueError(
                    f"Received unknown prompt option for \
                        commissioning step: {prompt_response.response}"
                )

    async def __prompt_user_to_perform_decommission(self) -> None:
        """Prompt the user to perform decommission using a controller"""

        options = {
            "Decommission successful": PromptOption.PASS,
            "Decommission Failed": PromptOption.FAIL,
        }
        prompt = """Please decommission with the device using a controller:
                Example:
                    <Controller> pairing unpair <nodeid>
                """
        prompt_request = OptionsSelectPromptRequest(
            prompt=prompt, options=options, timeout=60
        )
        prompt_response = await self.send_prompt_request(prompt_request)

        match prompt_response.response:
            case PromptOption.FAIL:
                logger.info("User stated decommissioning step FAILED.")

            case PromptOption.PASS:
                logger.info("User stated decommissioning step PASSED.")

            case _:
                logger.info(
                    f"Received unknown prompt option for \
                        decommissioning step: {prompt_response.response}"
                )
