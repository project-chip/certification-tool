import os
from pathlib import Path
from unittest import mock

import pytest

from app import utils
from app.core.config import settings
from app.version import (
    SHA_FILEPATH,
    VERSION_FILEPATH,
    read_test_harness_backend_version,
)


def _write_contents_to_file(filepath: Path, contents: str) -> None:
    f = open(filepath, "w")
    f.write(contents)
    f.close()


def _remove_file(filepath: Path) -> None:
    if os.path.exists(path=filepath):
        os.remove(path=filepath)


@pytest.mark.serial
def test_read_test_harness_backend_version() -> None:
    expected_db_revision = "aabbccdd"  # spell-checker:disable-line
    expected_version_value = "v0.99"
    expected_sha_value = "0fb2dd9"

    _write_contents_to_file(VERSION_FILEPATH, expected_version_value)
    _write_contents_to_file(SHA_FILEPATH, expected_sha_value)

    with mock.patch.object(
        target=utils,
        attribute="get_db_revision",
        return_value=expected_db_revision,
    ) as mock_utils:
        backend_version = read_test_harness_backend_version()
        assert backend_version.version == expected_version_value
        assert backend_version.sha == expected_sha_value
        assert backend_version.sdk_sha == settings.SDK_SHA[:7]
        assert backend_version.db_revision == expected_db_revision

    mock_utils.assert_called_once()


@pytest.mark.serial
def test_read_test_harness_backend_version_with_empty_files() -> None:
    expected_version_value = "Unknown"
    expected_sha_value = "Unknown"

    _write_contents_to_file(VERSION_FILEPATH, "")
    _write_contents_to_file(SHA_FILEPATH, "")

    backend_version = read_test_harness_backend_version()
    assert backend_version.version == expected_version_value
    assert backend_version.sha == expected_sha_value
    assert backend_version.sdk_sha == settings.SDK_SHA[:7]


@pytest.mark.serial
def test_read_test_harness_backend_version_with_missing_files() -> None:
    expected_version_value = "Unknown"
    expected_sha_value = "Unknown"

    # Remove files if it exists
    _remove_file(filepath=VERSION_FILEPATH)
    _remove_file(filepath=SHA_FILEPATH)

    backend_version = read_test_harness_backend_version()
    assert backend_version.version == expected_version_value
    assert backend_version.sha == expected_sha_value
    assert backend_version.sdk_sha == settings.SDK_SHA[:7]
