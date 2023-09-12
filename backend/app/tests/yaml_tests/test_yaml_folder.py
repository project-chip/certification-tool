from pathlib import Path
from unittest import mock

from test_collections.yaml_tests.models.yaml_test_folder import YamlTestFolder

test_yaml_path = Path("/test/yaml")


def test_yaml_folder_version() -> None:
    version_file_path = test_yaml_path / ".version"
    version_file_content = "yaml_version"

    # We mock open to read version_file_content and Path exists to ignore that we're
    # testing with a fake path
    with mock.patch(
        "test_collections.yaml_tests.models.yaml_test_folder.open",
        new=mock.mock_open(read_data=version_file_content),
    ) as file_open, mock.patch.object(
        target=Path, attribute="exists", return_value=True
    ) as _:
        yaml_folder = YamlTestFolder(test_yaml_path)
        file_open.assert_called_once_with(version_file_path, "r")

        assert yaml_folder.version == version_file_content


def test_yaml_folder_version_missing() -> None:
    expected_version = "Unknown"
    yaml_folder = YamlTestFolder(test_yaml_path)
    assert yaml_folder.version == expected_version


def test_yaml_folder_filename_pattern() -> None:
    """Test YamlTestFolder will search for files with filename pattern."""
    with mock.patch.object(target=Path, attribute="glob") as path_glob:
        # Default file_name_patter: *
        yaml_folder = YamlTestFolder(test_yaml_path)
        _ = yaml_folder.yaml_file_paths()
        path_glob.assert_called_once_with("*.y*ml")

        path_glob.reset_mock()
        pattern = "TC_*"
        yaml_folder = YamlTestFolder(test_yaml_path, filename_pattern=pattern)
        _ = yaml_folder.yaml_file_paths()
        path_glob.assert_called_once_with(f"{pattern}.y*ml")
