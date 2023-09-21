import asyncio
import os
import re
from asyncio.tasks import wait_for
from os.path import exists
from pathlib import Path
from typing import Any, Generator, Optional

from docker.models.containers import Container
from loguru import logger

from app.container_manager import container_manager
from app.schemas.test_environment_config import ThreadAutoConfig
from app.singleton import Singleton

DEFAULT_DOCKER_IMAGE = "connectedhomeip/otbr:sve2"

APP_PATH = Path(__file__).parent.parent.resolve()
BACKEND_DOCKER_OTBR_DIRNAME = Path(__file__).resolve().parent.relative_to(APP_PATH)
OTBR_AVAHI_DIRNAME = "avahi"


OTBR_STARTUP_TIMEOUT = 200  # 3min 20s. Users reported up to 3min used for startup.
OTBR_READINESS_EXTRA_TIME = 10  # 10s added after OTBR Form Topology


class ThreadBorderRouterError(Exception):
    pass


class ThreadBorderRouter(metaclass=Singleton):
    """
    Base class for Simulated Border Router to be used during test case execution.

    Usage:
    Create an instance by calling initializer. When ready to use, start the device by
    calling start_device and when done cleanup by calling destroy_device
    """

    tool_network_name = "host"
    run_parameters: dict[str, Any] = {
        "privileged": True,
        "detach": True,
        "network": tool_network_name,
        "environment": ["NAT64=1", "DNS64=0", "WEB_GUI=0"],
    }

    def __init__(self) -> None:
        self.__otbr_docker: Optional[Container] = None
        self.__docker_image = DEFAULT_DOCKER_IMAGE
        self

    def __load_config(self, config: ThreadAutoConfig) -> None:
        logger.debug("Loading thread network configuration")
        logger.debug(f"Loaded config: {config}")

        if not exists(config.rcp_serial_path):
            raise ThreadBorderRouterError(
                "Unable to start OTBR as rpc serial path: "
                f"{config.rcp_serial_path} does not exist. Change in settings."
            )

        backend_filepath_on_host = os.getenv("BACKEND_FILEPATH_ON_HOST")
        if backend_filepath_on_host is None:
            raise ThreadBorderRouterError(
                "Failed to start OTBR as `BACKEND_FILEPATH_ON_HOST` is not set. "
                "This should be set when starting test harness."
            )

        otbr_path = Path(backend_filepath_on_host) / BACKEND_DOCKER_OTBR_DIRNAME
        otbr_avahi_path = otbr_path / OTBR_AVAHI_DIRNAME

        self.run_parameters["volumes"] = {
            f"{config.rcp_serial_path}": {"bind": "/dev/radio"},
            otbr_avahi_path: {"bind": "/etc/avahi"},
        }
        baudrate = config.rcp_baudrate
        self.run_parameters["command"] = " ".join(
            [
                "--radio-url",
                f"spinel+hdlc+uart:///dev/radio?uart-baudrate={baudrate}",
                "-B",
                config.network_interface,
            ]
        )
        self.__dataset = config.dataset
        self.__on_mesh_prefix = config.on_mesh_prefix

        if config.otbr_docker_image is not None:
            self.__docker_image = config.otbr_docker_image
            logger.warning(
                f"Overriding default OTBR docker image with '{self.__docker_image}'."
            )

    def is_running(self) -> bool:
        if self.__otbr_docker is None:
            return False
        else:
            return container_manager.is_running(self.__otbr_docker)

    async def start_device(self, config: ThreadAutoConfig) -> bool:
        """
        start_device: Creates the device container with connected RCP.
        Returns true when a new container is created and all border router services
        are running.
        Return false, if container is already running.
        """
        if self.is_running():
            logger.warning(
                "OTBR container is already running for " + self.__docker_image
            )
            return False

        self.__load_config(config)
        logger.info(f"Starting OTBR via docker image: {self.__docker_image}")

        # Async return when the container is running
        self.__otbr_docker = await container_manager.create_container(
            self.__docker_image, self.run_parameters
        )

        try:
            await wait_for(self.__is_border_router_running(), OTBR_STARTUP_TIMEOUT)

        except asyncio.exceptions.TimeoutError:
            err_msg = "Border router does not start properly for " + self.__docker_image
            logger.error(err_msg)
            self.destroy_device()
            raise ThreadBorderRouterError(err_msg)

        logger.info(
            f"""
            Border Router started: {self.__otbr_docker.name}
            with configuration: {self.run_parameters}
            """
        )
        self.isRunning = True
        return self.isRunning

    async def __is_border_router_running(self) -> None:
        for chunk in self.__otbr_docker.logs(stream=True):  # type: ignore
            logger.debug(chunk)
            if b"Border router agent started" in chunk:
                return
            await asyncio.sleep(0.0001)

    @staticmethod
    def __gather_response(response: Generator) -> bytes:
        _SUCCESS_PATTERN = re.compile(r"((?:\r+\n|)Done\r+\n)$".encode())
        output = b""
        for i in response:
            output += i
            logger.debug("response: " + i.decode().strip())
        match_success = re.search(_SUCCESS_PATTERN, output)
        if match_success:
            output = output[: -len(match_success.group(1))]
        return output

    def _send_command(self, command: str, prefix: str = "ot-ctl") -> bytes:
        cmd = f"{prefix} {command}"
        logger.debug("sent:" + cmd)
        response = self.__otbr_docker.exec_run(cmd, stream=True)  # type: ignore
        return self.__gather_response(response.output)

    @property
    def network_id(self) -> str:
        return self.__dataset.extpanid

    @property
    def on_mesh_prefix(self) -> str:
        return self.__on_mesh_prefix

    @property
    def active_dataset(self) -> str:
        return self._send_command("dataset active -x").decode()

    async def form_thread_topology(self) -> None:
        self._send_command("dataset init new")
        self._send_command(f"dataset channel {self.__dataset.channel}")
        self._send_command(f"dataset panid {self.__dataset.panid}")
        self._send_command(f"dataset extpanid {self.__dataset.extpanid}")
        self._send_command(f"dataset networkkey {self.__dataset.networkkey}")
        self._send_command(f"dataset networkname {self.__dataset.networkname}")
        self._send_command("dataset commit active")
        self._send_command("ifconfig up")
        self._send_command("thread start")
        self._send_command(f"prefix add {self.__on_mesh_prefix} pasor")
        self._send_command("netdata register")

        # Allow OTBR extra time to form the network, before attempting to use.
        await asyncio.sleep(OTBR_READINESS_EXTRA_TIME)

    def destroy_device(self) -> None:
        """Destroy the device container and associated rpc client."""
        if self.__otbr_docker is None:
            logger.error("Container was never created for" + self.__docker_image)
            return

        if self.is_running():
            self._send_command("service otbr-firewall stop", prefix="")

        container_manager.destroy(self.__otbr_docker)
        self.__otbr_docker = None
