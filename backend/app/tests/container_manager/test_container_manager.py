from asyncio import TimeoutError
from unittest import mock

import pytest
from docker.errors import NotFound

from app.container_manager.container_manager import container_manager
from app.tests.utils.docker import Container, make_fake_container

DEFAULT_MOUNT_SRC = "/test/path/chip-cert-tool/backend"
DEFAULT_MOUNT_WORKING_DIR = "/app"


@pytest.mark.asyncio
async def test_create_container() -> None:
    with mock.patch(
        "docker.models.containers.ContainerCollection.run"
    ) as docker_run, mock.patch(
        "app.container_manager.container_manager.is_running",
        return_value=True,
    ):
        await container_manager.create_container(docker_image_tag="org/image:tag")
        docker_run.assert_called_once()


@pytest.mark.asyncio
async def test_create_container_timeout() -> None:
    with mock.patch("docker.models.containers.ContainerCollection.run"), mock.patch(
        "app.container_manager.container_manager.is_running",
        return_value=False,
    ):
        with pytest.raises(TimeoutError):
            await container_manager.create_container(docker_image_tag="org/image:tag")


def test_get_container_found() -> None:
    with mock.patch(
        "docker.models.containers.ContainerCollection.get",
        return_value=make_fake_container(),
    ):
        container = container_manager.get_container("test_name")
        assert container is not None


def test_get_container_not_found() -> None:
    with mock.patch(
        "docker.models.containers.ContainerCollection.get",
        side_effect=NotFound("Fake container not found error"),
    ):
        container = container_manager.get_container("test_name")
        assert container is None


def test_container_is_running() -> None:
    with mock.patch(
        "app.container_manager.container_manager.get_container",
        return_value=make_fake_container({"State": {"Status": "running"}}),
    ):
        assert container_manager.is_running(Container()) is True


def test_container_is_not_running() -> None:
    with mock.patch(
        "app.container_manager.container_manager.get_container",
        return_value=make_fake_container({"State": {"Status": "stopped"}}),
    ):
        assert container_manager.is_running(Container()) is False


def test_get_working_dir() -> None:
    working_dir = "/test"
    container = make_fake_container({"Config": {"WorkingDir": working_dir}})
    assert container_manager.get_working_dir(container) == working_dir


def test_get_working_dir_none() -> None:
    container = make_fake_container({"Config": {}})
    assert container_manager.get_working_dir(container) is None

    container = make_fake_container()
    assert container_manager.get_working_dir(container) is None


def test_get_mount_source_for_destination() -> None:
    test_source = "/host/path"
    test_dest = "/container/path"
    container = make_fake_container(
        attrs={
            "Mounts": [{"Source": test_source, "Destination": test_dest}],
        }
    )
    # Test existing mount destination
    src = container_manager.get_mount_source_for_destination(
        container, destination=test_dest
    )
    assert src == test_source

    # Test missing mount destination
    src = container_manager.get_mount_source_for_destination(
        container, destination="/missing/dest"
    )
    assert src is None


def test_get_mount_source_for_destination_no_mount() -> None:
    src = container_manager.get_mount_source_for_destination(
        make_fake_container(), destination="/some/path"
    )
    assert src is None


def test_get_mount_source_for_destination_invalid_attrs() -> None:
    test_dest = "/container/path"
    container = make_fake_container(
        attrs={
            "Mounts": [{"No-Source": None, "Destination": test_dest}],
        }
    )

    src = container_manager.get_mount_source_for_destination(
        container, destination=test_dest
    )
    assert src is None
