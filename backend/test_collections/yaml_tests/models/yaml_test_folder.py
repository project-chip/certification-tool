from pathlib import Path

UNKNOWN_version = "Unknown"
VERSION_FILE_FILENAME = ".version"


class YamlTestFolder:
    """Representing a folder with Test YAML files.

    Note: YAML version is read from .version file in folder on init.
    """

    def __init__(self, path: Path, filename_pattern: str = "*") -> None:
        self.path = path
        self.filename_pattern = filename_pattern
        self.version = self.__version()

    def __version(self) -> str:
        """Read version string from .version file in same folder as yaml files."""
        version_file_path = self.path / VERSION_FILE_FILENAME

        if not version_file_path.exists():
            return UNKNOWN_version
        else:
            with open(version_file_path, "r") as file:
                return file.read().rstrip()

    def yaml_file_paths(self) -> list[Path]:
        """Get list of paths to yaml files in folder.

        Filename filter can be applied if only some files should be selected.
        Note: filter is without extension. Will search for .yml and .yaml files

        Args:
            filename_pattern (str, optional): custom file filter. Defaults to "*".

        Returns:
            list[Path]: list of paths to YAML test files.
        """
        return list(self.path.glob(self.filename_pattern + ".y*ml"))
