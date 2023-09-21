from pathlib import Path

from .models.test_declarations import (
    YamlCaseDeclaration,
    YamlCollectionDeclaration,
    YamlSuiteDeclaration,
)
from .models.test_suite import SuiteType
from .models.yaml_test_folder import YamlTestFolder
from .models.yaml_test_models import YamlTestType
from .models.yaml_test_parser import parse_yaml_test

###
# This file hosts logic load and parse YAML test-cases, located in
# `test_collections/yaml_tests/yaml/sdk`. The `sdk` sub-folder here is automatically
# maintained using the `scripts/fetch_sdk_yaml_tests_and_runner.sh` script.
#
# The YAML Tests are organized into 3 Test Suites:
#        - Automated and Semi-Automated using Chip-Tool
#        - Simulated using Chip-App1
#        - Manual
###

SDK_YAML_PATH = Path(__file__).parent / "yaml" / "sdk"
SDK_YAML_TEST_FOLDER = YamlTestFolder(path=SDK_YAML_PATH, filename_pattern="Test_TC*")


def _init_test_suites(yaml_version: str) -> dict[SuiteType, YamlSuiteDeclaration]:
    return {
        SuiteType.MANUAL: YamlSuiteDeclaration(
            name="FirstManualSuite",
            suite_type=SuiteType.MANUAL,
            version=yaml_version,
        ),
        SuiteType.AUTOMATED: YamlSuiteDeclaration(
            name="FirstChipToolSuite",
            suite_type=SuiteType.AUTOMATED,
            version=yaml_version,
        ),
        SuiteType.SIMULATED: YamlSuiteDeclaration(
            name="FirstAppSuite",
            suite_type=SuiteType.SIMULATED,
            version=yaml_version,
        ),
    }


def _parse_yaml_to_test_case_declaration(
    yaml_path: Path, yaml_version: str
) -> YamlCaseDeclaration:
    yaml_test = parse_yaml_test(yaml_path)
    return YamlCaseDeclaration(test=yaml_test, yaml_version=yaml_version)


def _parse_all_sdk_yaml(
    yaml_files: list[Path], yaml_version: str
) -> list[YamlSuiteDeclaration]:
    """Parse all yaml files and organize them in the 3 test suites:
    - Automated and Semi-Automated using Chip-Tool
    - Simulated using Chip-App1
    - Manual
    """
    suites = _init_test_suites(yaml_version)

    for yaml_file in yaml_files:
        test_case = _parse_yaml_to_test_case_declaration(
            yaml_path=yaml_file, yaml_version=yaml_version
        )

        if test_case.test_type == YamlTestType.MANUAL:
            suites[SuiteType.MANUAL].add_test_case(test_case)
        elif test_case.test_type == YamlTestType.SIMULATED:
            suites[SuiteType.SIMULATED].add_test_case(test_case)
        else:
            suites[SuiteType.AUTOMATED].add_test_case(test_case)

    return list(suites.values())


def sdk_yaml_test_collection(
    yaml_test_folder: YamlTestFolder = SDK_YAML_TEST_FOLDER,
) -> YamlCollectionDeclaration:
    """Declare a new collection of test suites with the 3 test suites."""
    collection = YamlCollectionDeclaration(
        name="SDK YAML Tests", folder=yaml_test_folder
    )

    files = yaml_test_folder.yaml_file_paths()
    version = yaml_test_folder.version
    suites = _parse_all_sdk_yaml(yaml_files=files, yaml_version=version)

    for suite in suites:
        suite.sort_test_cases()
        collection.add_test_suite(suite)

    return collection
