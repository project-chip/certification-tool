import asyncio
from asyncio import TimeoutError, wait_for
from typing import Dict, Optional

import docker
from docker.errors import DockerException, NotFound
from docker.models.containers import Container
from loguru import logger

from app.singleton import Singleton

# Note: Can we use a base docker image and single RPC process(OR a Bash script) entry
# point to later configure the image to be a particular type
container_bring_up_timeout = 5  # Seconds


class ContainerManager(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.__client = docker.from_env()

    async def create_container(
        self, docker_image_tag: str, parameters: Dict = {}
    ) -> Container:
        container = self.__run_new_container(docker_image_tag, parameters)
        await self.__container_ready(container)
        logger.info("Container running for " + docker_image_tag)

        return container

    def destroy(self, container: Container) -> None:
        if self.is_running(container):
            container.kill()
        container.remove()

    def get_container(self, id_or_name: str) -> Optional[Container]:
        try:
            return self.__client.containers.get(id_or_name)
        except NotFound:
            logger.info(f"Did not find container by id or name: {id_or_name}.")
            return None

    def is_running(self, container: Container) -> bool:
        # NOTE: we need to get a new container reference to get updated status.
        if c := self.get_container(container.id):
            return c.status == "running"
        else:
            return False

    def get_working_dir(self, container: Container) -> Optional[str]:
        """Lookup containers WorkingDir from it's config."""
        if config := container.attrs.get("Config"):
            if working_dir := config.get("WorkingDir"):
                return working_dir

        return None

    def get_mount_source_for_destination(
        self, container: Container, destination: str
    ) -> Optional[str]:
        """Find mount source for a mount destination."""
        if mounts := container.attrs.get("Mounts"):
            # Return first mount source with mount destination we're searching for.
            return next(
                (
                    m.get("Source")
                    for m in mounts
                    if m.get("Destination") == destination
                ),
                None,
            )

        return None

    # Internal Methods
    def __run_new_container(self, docker_image_tag: str, parameters: Dict) -> Container:
        # Create containers
        try:
            return self.__client.containers.run(docker_image_tag, **parameters)
        except DockerException as error:
            logger.error(
                "Error ocurred while creating a container from image " + str(error)
            )
            raise error

    async def __container_ready(self, container: Container) -> None:
        # Wait for the container for start running
        try:
            await wait_for(
                self.__container_started(container), container_bring_up_timeout
            )
        except TimeoutError as e:
            logger.error(
                f"Container did start timed out in {container_bring_up_timeout}s"
            )
            self.destroy(container)
            raise e

    async def __container_started(self, container: Container) -> None:
        sleep_interval = 0.2

        while True:
            # Check if the container is running, then sleep for 0.1 sec
            if self.is_running(container):
                return

            # Sleep first to give container some time
            await asyncio.sleep(sleep_interval)


container_manager = ContainerManager()
