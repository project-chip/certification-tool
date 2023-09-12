import socket
from pathlib import Path
from typing import Optional

from docker.models.containers import Container

from .container_manager import container_manager

BACKEND_MOUNT_DEST = "/app"


class BackendContainerError(Exception):
    pass


def __backend_container_id() -> str:
    """Docker container id is by default available inside a container as the hostname.

    See https://docs.docker.com/config/containers/container-networking/
    """
    return socket.gethostname()


def backend_container() -> Optional[Container]:
    """Get the Docker Container for backend."""
    return container_manager.get_container(__backend_container_id())


def backend_mount_on_host() -> Path:
    """Get the full path to the backend folder on the Host filesystem.

    The docker config "WorkingDir" for backend container is the backend root folder.
    However, this folder might not be mounted directly in docker.

    The source code mount destination in backend container is always `/app`. But the
    "WorkingDir" can be either `/app` or `/app/backend` depending on how the test
    harness is started.

    By default, the `backend` folder is mounted as `/app` inside the backend docker
    container. However, when using `scripts/start-dev.sh` the test harness root project
    folder is is mounted at `app`, this is to enable git access from inside the
    backend container.

    Algorithm:
        Assume test harness code is checkout at /home/ubuntu/chip-certification-tool

        1. Get mount source for source code mount (/app)
            example1: /home/ubuntu/chip-certification-tool
            example2: /home/ubuntu/chip-certification-tool/backend
        2. Get workingDir
            example1: /app/backend
            example2: /app
        3. Get relative path to WorkingDir from /app
            example1: backend
            example2: .
        4. Get full path to backend folder on host system by appending relative path to
        backend folder to source path for source code mount
            example1: /home/ubuntu/chip-certification-tool + /backend
            example2: /home/ubuntu/chip-certification-tool/backend + /.
    """

    if (backend := backend_container()) is None:
        raise BackendContainerError("Could not find backend container")

    if (
        mount_source := container_manager.get_mount_source_for_destination(
            container=backend, destination=BACKEND_MOUNT_DEST
        )
    ) is None:
        raise BackendContainerError("Couldn't find backend source-code mount")

    if (working_dir := container_manager.get_working_dir(backend)) is None:
        raise BackendContainerError("Couldn't find backend mount")

    backend_relative_dir = Path(working_dir).relative_to(BACKEND_MOUNT_DEST)
    backend_dir_on_host = Path(mount_source) / backend_relative_dir

    return backend_dir_on_host
