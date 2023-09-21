from __future__ import annotations

import json
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from random import randrange
from typing import Any, Generator, Optional, Union, cast

import loguru
from docker.models.containers import Container
from matter_chip_tool_adapter import adapter as ChipToolAdapter
from matter_chip_tool_adapter.decoder import MatterLog
from matter_placeholder_adapter import adapter as ChipAppAdapter
from matter_yamltests.definitions import SpecDefinitionsFromPaths
from matter_yamltests.hooks import TestRunnerHooks

# Matter YAML tests Imports
from matter_yamltests.parser import TestParserConfig
from matter_yamltests.parser_builder import TestParserBuilderConfig
from matter_yamltests.pseudo_clusters.pseudo_clusters import get_default_pseudo_clusters
from matter_yamltests.runner import TestRunnerConfig, TestRunnerOptions
from matter_yamltests.websocket_runner import WebSocketRunner, WebSocketRunnerConfig

from app.container_manager import container_manager
from app.container_manager.backend_container import backend_container
from app.core.config import settings
from app.schemas.pics import PICS, PICSError
from app.singleton import Singleton
from app.test_engine.logger import CHIP_LOG_FORMAT, CHIPTOOL_LEVEL
from app.test_engine.logger import test_engine_logger as logger

from .exec_run_in_container import ExecResultExtended, exec_run_in_container

# Chip Tool Parameters
CHIP_TOOL_EXE = "./chip-tool"
CHIP_TOOL_ARG_NODEID = "nodeId"
CHIP_TOOL_ARG_DELAY = "delayInMs"
CHIP_TOOL_ARG_PICS = "--PICS"
CHIP_TOOL_ARG_ENDPOINT_ID = "--endpoint"
CHIP_TOOL_ARG_TIMEOUT = "timeout"
CHIP_TOOL_TEST_DEFAULT_TIMEOUT_IN_SEC = "900"  # 15 minutes (60*15 seconds)
CHIP_TOOL_ARG_PAA_CERTS_PATH = "--paa-trust-store-path"
CHIP_TOOL_CONTINUE_ON_FAILURE_VALUE = True

TESTS_CMD = "tests"
PAIRING_CMD = "pairing"
PAIRING_MODE_CODE = "code"
PAIRING_MODE_ONNETWORK = "onnetwork-long"
PAIRING_MODE_BLE_WIFI = "ble-wifi"
PAIRING_MODE_BLE_THREAD = "ble-thread"
PAIRING_MODE_UNPAIR = "unpair"
TEST_STEP_DELAY_VALUE = 250


# Chip App Parameters
CHIP_APP_EXE = "./chip-app1"
CHIP_APP_PORT_ARG = "--secured-device-port"
CHIP_APP_DEFAULT_PORT = 5540
CHIP_APP_TEST_CMD_ARG = "--command"

# PICS parameters
SHELL_PATH = "/bin/sh"
SHELL_OPTION = "-c"
PICS_FILE_PATH = "/var/tmp/pics"
ECHO_COMMAND = "echo"
# List of default PICS which needs to set specifically in TH are added here.
# These PICS are applicable for CI / Chip tool testing purposes only.
# These PICS are unknown / not visible to external users.
DEFAULT_PICS = ["PICS_SDK_CI_ONLY=0", "PICS_SKIP_SAMPLE_APP=1", "PICS_USER_PROMPT=1"]

# Trace mount
LOCAL_LOGS_PATH = Path("/var/tmp")
DOCKER_LOGS_PATH = "/logs"

# PAA Cert mount
LOCAL_PAA_CERTS_PATH = Path("/var/paa-root-certs")
DOCKER_PAA_CERTS_PATH = "/paa-root-certs"

# Websocket runner
BACKEND_ROOT = Path(__file__).parents[2]
YAML_TESTS_PATH_BASE = BACKEND_ROOT / Path("test_collections/yaml_tests/")
YAML_TESTS_PATH = YAML_TESTS_PATH_BASE / Path("yaml/sdk")
XML_SPEC_DEFINITION_PATH = YAML_TESTS_PATH_BASE / Path(
    "sdk_runner/specifications/chip/"
)


# Docker Network
DOCKER_NETWORK_SETTINGS_KEY = "NetworkSettings"
DOCKER_NETWORKS_KEY = "Networks"
DOCKER_CHIP_DEFAULT_KEY = "chip-default"
DOCKER_GATEWAY_KEY = "Gateway"


class ChipToolStartingError(Exception):
    """Raised when we fail to start the chip-tool docker container"""


class ChipToolNotRunning(Exception):
    """Raised when we attempt to use chip-tool, but docker container is not running"""


class ChipToolUnknownTestType(Exception):
    """Raised when we attempt to use chip-tool, but test(executable) type is not
    supported"""


class ChipToolTestType(str, Enum):
    CHIP_TOOL = "chip-tool"
    CHIP_APP = "chip-app"


class ChipTool(metaclass=Singleton):
    """
    Base class for Chip Tool to be used during test case execution.

    Usage:
    Create an instance by calling initializer. When ready to use, start the device by
    calling start_device and when done cleanup by calling destroy_device
    """

    container_name = settings.CHIP_TOOL_CONTAINER_NAME
    image_tag = f"{settings.SDK_DOCKER_IMAGE}:{settings.SDK_DOCKER_TAG}"
    run_parameters = {
        "privileged": True,
        "detach": True,
        "network": "host",
        "name": container_name,
        "command": "tail -f /dev/null",  # while true
        "volumes": {
            "/var/run/dbus/system_bus_socket": {
                "bind": "/var/run/dbus/system_bus_socket",
                "mode": "rw",
            },
            LOCAL_LOGS_PATH: {
                "bind": DOCKER_LOGS_PATH,
                "mode": "rw",
            },
            LOCAL_PAA_CERTS_PATH: {
                "bind": DOCKER_PAA_CERTS_PATH,
                "mode": "ro",
            },
        },
    }

    __node_id: Optional[int]  # will be reset every time the container is started
    __pics_file_created: bool  # Flag that is set if PICS needs to be passed to chiptool

    def __init__(
        self,
        logger: loguru.Logger = logger,
    ) -> None:
        """Chip-Tool run chip-tool commands in Docker container.

        Args:
            logger (Logger, optional): Optional logger injection. Defaults to standard
            self.logger.
        """
        self.__chip_tool_container: Optional[Container] = None

        # Last execution id is updated every time a command is executed
        # This is used to retrieve the exit code of a command when streaming the logs.
        self.__last_exec_id: Optional[str] = None
        self.__pics_file_created = False
        self.logger = logger
        self.__chip_tool_server_id: Optional[str] = None
        self.__server_started = False
        self.__server_logs: Union[Generator, bytes, tuple]
        self.__use_paa_certs = False
        self.__test_type: ChipToolTestType = ChipToolTestType.CHIP_TOOL
        # TODO: Need to dynamically select the specs based on clusters in test.
        specifications_paths = [f"{XML_SPEC_DEFINITION_PATH}/*.xml"]
        self.pseudo_clusters = get_default_pseudo_clusters()
        self.specifications = SpecDefinitionsFromPaths(
            specifications_paths, self.pseudo_clusters
        )

    @property
    def node_id(self) -> int:
        """Node id is used to reference DUT during testing.

        Returns:
            int: unit64 node id
        """

        if self.__node_id is None:
            return self.__reset_node_id()

        return self.__node_id

    def __reset_node_id(self) -> int:
        """Resets node_id to a random uint64."""
        max_uint_64 = (1 << 64) - 1
        self.__node_id = randrange(max_uint_64)
        return self.__node_id

    def __destroy_existing_container(self) -> None:
        """This will kill and remove any existing container using the same name."""
        existing_container = container_manager.get_container(self.container_name)
        if existing_container is not None:
            logger.info(
                f'Existing container named "{self.container_name}" found. Destroying.'
            )
            container_manager.destroy(existing_container)

    def is_running(self) -> bool:
        if self.__chip_tool_container is None:
            return False
        else:
            return container_manager.is_running(self.__chip_tool_container)

    async def __wait_for_server_start(self, log_generator: Generator) -> bool:
        for chunk in log_generator:
            decoded_log = chunk.decode().strip()
            log_lines = decoded_log.splitlines()
            for line in log_lines:
                if "LWS_CALLBACK_PROTOCOL_INIT" in line:
                    logger.log(CHIPTOOL_LEVEL, line)
                    return True
                logger.log(CHIPTOOL_LEVEL, line)
        else:
            return False

    async def start_chip_server(
        self, test_type: ChipToolTestType, use_paa_certs: bool = False
    ) -> Generator:
        # Start ChipTool Interactive Server
        self.__use_paa_certs = use_paa_certs
        self.__test_type = test_type
        self.logger.info("Starting Chip Tool Server")
        if self.__server_started:
            return cast(Generator, self.__server_logs)

        if test_type == ChipToolTestType.CHIP_TOOL:
            prefix = CHIP_TOOL_EXE
            command = ["interactive", "server"]
        elif test_type == ChipToolTestType.CHIP_APP:
            prefix = CHIP_APP_EXE
            command = ["--interactive", "--port 9002"]
        else:
            raise ChipToolUnknownTestType(f"Unsupported Test Type: {test_type}")

        if settings.CHIP_TOOL_TRACE:
            topic = "CHIP_TOOL_WEBSOCKET_SERVER"
            command.append(self.__trace_file_params(topic))

        if use_paa_certs:
            paa_cert_params = f"{CHIP_TOOL_ARG_PAA_CERTS_PATH} {DOCKER_PAA_CERTS_PATH}"
            command.append(paa_cert_params)

        self.__server_logs = self.send_command(
            command,
            prefix=prefix,
            is_stream=True,
            is_socket=False,
        ).output
        self.__chip_tool_server_id = self.__last_exec_id
        wait_result = await self.__wait_for_server_start(
            cast(Generator, self.__server_logs)
        )
        if not wait_result:
            raise ChipToolStartingError("Unable to start chip-tool server")
        self.__server_started = True
        return cast(Generator, self.__server_logs)

    def __wait_for_server_exit(self) -> Optional[int]:
        exit_code = None
        if self.__chip_tool_container is None:
            self.logger.info(
                "No chip-tool container, cannot return last command exit code."
            )
            return None

        if self.__chip_tool_server_id is None:
            self.logger.info(
                "Last execution id not found, cannot return last command exit code."
            )
            return None

        while True:
            exec_data = self.__chip_tool_container.client.api.exec_inspect(
                self.__chip_tool_server_id
            )
            if exec_data is None:
                self.logger.error(
                    "Docker didn't return any execution metadata,"
                    " cannot return last command exit code."
                )
                return None
            exit_code = exec_data.get("ExitCode")
            if exit_code is not None:
                break

        return exit_code

    async def stop_chip_tool_server(self) -> None:
        await self.__test_harness_runner.start()
        await self.__test_harness_runner._client.send("quit()")
        self.__wait_for_server_exit()
        self.__server_started = False

    def __get_gateway_ip(self) -> str:
        """
        Obtains the IP address from the backend gateway.

        Returns:
            str: IP address of the gateway within the th-chip-tool container
        """
        backend_container_obj = backend_container()
        if backend_container_obj is None:
            raise ChipToolNotRunning("Backend container not running")

        return (
            backend_container_obj.attrs.get(DOCKER_NETWORK_SETTINGS_KEY, {})
            .get(DOCKER_NETWORKS_KEY, {})
            .get(DOCKER_CHIP_DEFAULT_KEY, {})
            .get(DOCKER_GATEWAY_KEY, "")
        )

    async def start_container(
        self, test_type: ChipToolTestType, use_paa_certs: bool = False
    ) -> None:
        """Creates the chip-tool container.

        Returns only when the container is created and all chip-tool services start.
        """

        if self.is_running():
            self.logger.info(
                "chip-tool container already running, no need to start a new container"
            )
            return

        # Ensure there's no existing container running using the same name.
        self.__destroy_existing_container()

        # Async return when the container is running
        self.__chip_tool_container = await container_manager.create_container(
            self.image_tag, self.run_parameters
        )

        # Reset any previous states
        self.__last_exec_id = None
        self.__pics_file_created = False

        # Generate new random node id for the DUT
        self.__reset_node_id()
        self.logger.info(f"New Node Id generated: {hex(self.node_id)}")

        self.logger.info(
            f"""
            chip-tool started: {self.container_name}
            with configuration: {self.run_parameters}
            """
        )

        # Server started is false after spinning up a new container.
        self.__server_started = False

        web_socket_config = WebSocketRunnerConfig()
        web_socket_config.server_address = self.__get_gateway_ip()
        self.__test_harness_runner = WebSocketRunner(config=web_socket_config)

        self.__chip_tool_log = await self.start_chip_server(test_type, use_paa_certs)

    def destroy_device(self) -> None:
        """Destroy the device container."""
        if self.__chip_tool_container is not None:
            container_manager.destroy(self.__chip_tool_container)
        self.__chip_tool_container = None

    def send_command(
        self,
        command: Union[str, list],
        prefix: str,
        is_stream: bool = False,
        is_socket: bool = False,
    ) -> ExecResultExtended:
        if self.__chip_tool_container is None:
            raise ChipToolNotRunning()

        full_cmd = [prefix]
        if isinstance(command, list):
            full_cmd += command
        else:
            full_cmd.append(str(command))

        self.logger.info("Sending command to chip-tool: " + " ".join(full_cmd))

        result = exec_run_in_container(
            self.__chip_tool_container,
            " ".join(full_cmd),
            socket=is_socket,
            stream=is_stream,
            stdin=True,
        )

        # When streaming logs, the exit code is not directly available.
        # By storing the execution id, the exit code can be fetched from docker later.
        self.__last_exec_id = result.exec_id

        return ExecResultExtended(
            result.exit_code, result.output, result.exec_id, result.socket
        )

    def last_command_exit_code(self) -> Optional[int]:
        """Get the exit code of the last run command.

        When streaming logs from chip-tool in docker, the exit code is not directly
        available. Using the id of the execution, the exit code is fetched from docker.

        Returns:
            Optional[int]: exit code of the last run command
        """
        if self.__last_exec_id is None:
            self.logger.info(
                "Last execution id not found, cannot return last command exit code."
            )
            return None

        if self.__chip_tool_container is None:
            self.logger.info(
                "No chip-tool container, cannot return last command exit code."
            )
            return None

        exec_data = self.__chip_tool_container.client.api.exec_inspect(
            self.__last_exec_id
        )
        if exec_data is None:
            self.logger.error(
                "Docker didn't return any execution metadata,"
                " cannot return last command exit code."
            )
            return None

        exit_code = exec_data.get("ExitCode")
        return exit_code

    async def send_websocket_command(self, cmd: str) -> Union[str, bytes, bytearray]:
        response = None
        try:
            await self.__test_harness_runner.start()
            response = await self.__test_harness_runner.execute(cmd)
        finally:
            await self.__test_harness_runner.stop()

        # Log response
        if response:
            json_payload = json.loads(response)
            logs = MatterLog.decode_logs(json_payload.get("logs"))

            for log_entry in logs:
                self.logger.log(
                    CHIPTOOL_LEVEL,
                    CHIP_LOG_FORMAT.format(log_entry.module, log_entry.message),
                )

        return response

    # Chip Tool Command wrappers ###
    async def pairing(self, mode: str, *params: str, stream: bool = True) -> bool:
        command = [PAIRING_CMD, mode] + list(params)

        if settings.CHIP_TOOL_TRACE:
            topic = f"PAIRING_{mode}"
            command.append(self.__trace_file_params(topic))

        response = await self.send_websocket_command(" ".join(command))
        if not response:
            return False

        json_payload = json.loads(response)
        # TODO: Need to save logs maybe?
        # logs = MatterLog.decode_logs(json_payload.get('logs'))
        return not bool(
            len([lambda x: x.get("error") for x in json_payload.get("results")])
        )

    async def run_websocket_test(
        self,
        test_step_interface: TestRunnerHooks,
        adapter: Optional[Any],
        parser_builder_config: TestParserBuilderConfig,
    ) -> bool:
        stop_on_warning = False
        stop_at_number = -1
        stop_on_error = not CHIP_TOOL_CONTINUE_ON_FAILURE_VALUE
        runner_options = TestRunnerOptions(
            stop_on_error, stop_on_warning, stop_at_number, TEST_STEP_DELAY_VALUE
        )
        self.__runner_hooks = test_step_interface
        runner_config = TestRunnerConfig(
            adapter, self.pseudo_clusters, runner_options, test_step_interface
        )

        web_socket_config = WebSocketRunnerConfig()
        web_socket_config.server_address = self.__get_gateway_ip()
        self.__test_harness_runner = WebSocketRunner(config=web_socket_config)
        return await self.__test_harness_runner.run(
            parser_builder_config, runner_config
        )

    # TODO: Clean up duplicate function definition written to avoid unit test failures
    async def run_test(
        self,
        test_step_interface: TestRunnerHooks,
        test_id: str,
        test_type: ChipToolTestType,
        timeout: Optional[str] = None,
        test_parameters: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Run the test with the associated id using the right executable/container

        Args:
            test_id (str): Test Id to be run, must be available on the particular binary
            test_type (ChipToolTestType): Type of the binary that needs to be run

        Raises:
            ChipToolUnknownTestType: Unsupported type of test binary

        Yields:
            ExecResultExtended named tuple with the following information
            - exit_code
            - Union of Generator / bytes / tuple
            - exec_id
            - socket, when "is_socket" is set to True
        """
        if timeout is None:
            timeout = CHIP_TOOL_TEST_DEFAULT_TIMEOUT_IN_SEC

        test_options = {
            f"{CHIP_TOOL_ARG_NODEID}": f"{hex(self.node_id)}",
            f"{CHIP_TOOL_ARG_TIMEOUT}": f"{timeout}",
        }

        if test_parameters is not None and "endpoint" in test_parameters:
            test_options["endpoint"] = test_parameters["endpoint"]

        pics_path = None
        if self.__pics_file_created:
            pics_path = f"{PICS_FILE_PATH}"
            self.logger.info(f"Using PICS file: {pics_path}")

        if test_type == ChipToolTestType.CHIP_TOOL:
            test_path = f"{YAML_TESTS_PATH}/{test_id}.yaml"
        else:
            test_path = f"{YAML_TESTS_PATH}/{test_id}_Simulated.yaml"

        parser_config = TestParserConfig(pics_path, self.specifications, test_options)
        parser_builder_config = TestParserBuilderConfig([test_path], parser_config)

        if test_type == ChipToolTestType.CHIP_TOOL:
            adapter = ChipToolAdapter.Adapter(parser_config.definitions)
        elif test_type == ChipToolTestType.CHIP_APP:
            adapter = ChipAppAdapter.Adapter(parser_config.definitions)
        else:
            raise ChipToolUnknownTestType(f"Unsupported Test Type: {test_type}")

        return await self.run_websocket_test(
            test_step_interface, adapter, parser_builder_config
        )

    async def unpair(self) -> bool:
        return await self.pairing(
            PAIRING_MODE_UNPAIR,
            hex(self.node_id),
        )

    async def pairing_on_network(
        self,
        setup_code: str,
        discriminator: str,
    ) -> bool:
        return await self.pairing(
            PAIRING_MODE_ONNETWORK,
            hex(self.node_id),
            setup_code,
            discriminator,
        )

    async def pairing_ble_wifi(
        self,
        ssid: str,
        password: str,
        setup_code: str,
        discriminator: str,
    ) -> bool:
        return await self.pairing(
            PAIRING_MODE_BLE_WIFI,
            hex(self.node_id),
            ssid,
            password,
            setup_code,
            discriminator,
        )

    async def pairing_ble_thread(
        self,
        hex_dataset: str,
        setup_code: str,
        discriminator: str,
    ) -> bool:
        return await self.pairing(
            PAIRING_MODE_BLE_THREAD,
            hex(self.node_id),
            f"hex:{hex_dataset}",
            setup_code,
            discriminator,
        )

    def __trace_file_params(self, topic: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filename = f"trace_log_{timestamp}_{hex(self.node_id)}_{topic}.log"
        path = Path(DOCKER_LOGS_PATH) / filename
        return f'--trace_file "{path}" --trace_decode 1'

    def set_pics(self, pics: PICS) -> None:
        """Sends command to chip tool to create pics file inside the container.

        Args:
            pics (PICS): PICS that contains all the pics codes

        Raises:
            ChipToolNotRunning: Raises exception if chip tool is not running.
            PICSError: If creating PICS file inside the container fails.

        """
        # List of default PICS which needs to set specifically in TH are added here.
        # These PICS are applicable for CI / Chip tool testing purposes only.
        # These PICS are unknown / not visible to external users.

        pics_codes = self.__pics_file_content(pics) + "\n".join(DEFAULT_PICS)
        cmd = f"{SHELL_PATH} {SHELL_OPTION} "
        cmd = cmd + f"\"{ECHO_COMMAND} '{pics_codes}\n' > {PICS_FILE_PATH}\""
        self.logger.info(f"Sending command: {cmd}")
        result = subprocess.run(cmd, shell=True)

        # When streaming logs, the exit code is not directly available.
        # By storing the execution id, the exit code can be fetched from docker later.
        self.__last_exec_id = str(result.returncode)

        if result.returncode != 0:
            raise PICSError("Creating PICS file failed")

        self.__pics_file_created = True

    def reset_pics_state(self) -> None:
        self.__pics_file_created = False

    def __pics_file_content(self, pics: PICS) -> str:
        """Generates PICS file content in the below format:
           PICS_CODE1=1
           PICS_CODE2=1
           PICS_CODE3=0
           .....

        Args:
            pics (PICS): PICS that contains all the pics codes

        Returns:
            str: Returns a string in this format PICS_CODE1=1\nPICS_CODE1=2\n"
        """
        pics_str: str = ""

        for cluster in pics.clusters.values():
            for pi in cluster.items.values():
                if pi.enabled:
                    pics_str += pi.number + "=1" + "\n"
                else:
                    pics_str += pi.number + "=0" + "\n"

        return pics_str

    async def restart_server(self) -> None:
        await self.stop_chip_tool_server()
        self.__chip_tool_log = await self.start_chip_server(
            self.__test_type, self.__use_paa_certs
        )

    # TODO(#490): Need to be refactored to support real PIXIT format
    def __test_parameters_arguments(
        self, test_parameters: Optional[dict[str, Any]]
    ) -> list:
        """Generate cli arguments for chip-tool based on test_parameters.

        Note:
         - Currently `nodeID` is managed by this class, and should not be overridden
        by test_parameters.
         - chip-tool allows users to configure `cluster` via cli, but this should not
           be used.

        This method is ignoring `nodeID` and `cluster` from input argument
        `test_parameters`.

        chip-tool is expecting test_parameter arguments as
        `--<config-key> value`

        Args:
            test_parameters (Optional[dict[str, Any]]): dictionary of test parameters

        Returns:
            list: list of chip-tool arguments.
        """
        if test_parameters is None:
            return []

        arguments = []
        for name, value in test_parameters.items():
            # skip nodeId, as it is passed separately
            # skip cluster, as we don't allow to override this
            if name in ["nodeId", "cluster"]:
                continue

            if str(value) != "":
                # TODO: does this work for all formats, string, number etc?
                arguments.append(f"--{name} {str(value)}")
            else:
                arguments.append(f'--{name} ""')

        return arguments
