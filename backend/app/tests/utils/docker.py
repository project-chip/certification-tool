from typing import Optional
from unittest.mock import MagicMock

from docker.models.containers import Container

FAKE_ID = "ThisIsAFakeIdForADockerContainer"


def make_fake_container(
    attrs: Optional[dict] = {"Id": FAKE_ID}, mock_api_config: Optional[dict] = None
) -> Container:
    container = Container(attrs=attrs)

    if mock_api_config:
        container.client = MagicMock()
        container.client.api = MagicMock()
        container.client.api.configure_mock(**mock_api_config)

    return container
