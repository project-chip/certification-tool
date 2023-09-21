from pathlib import Path

import pytest

from test_collections.yaml_tests.models.test_declarations import (
    YamlCaseDeclaration,
    YamlCollectionDeclaration,
)
from test_collections.yaml_tests.models.yaml_test_folder import YamlTestFolder
from test_collections.yaml_tests.models.yaml_test_models import YamlTestType
from test_collections.yaml_tests.sdk_yaml_tests import sdk_yaml_test_collection


@pytest.fixture
def yaml_collection() -> YamlCollectionDeclaration:
    test_sdk_yaml_path = Path(__file__).parent / "test_yamls"
    folder = YamlTestFolder(path=test_sdk_yaml_path, filename_pattern="UnitTest_TC_*")
    return sdk_yaml_test_collection(folder)


def test_sdk_yaml_collection(yaml_collection: YamlCollectionDeclaration) -> None:
    assert yaml_collection.name == "SDK YAML Tests"
    assert len(yaml_collection.test_suites.keys()) == 3

    # test version number
    test_sdk_yaml_version_path = Path(__file__).parent / "test_yamls" / ".version"
    with open(test_sdk_yaml_version_path, "r") as version_file:
        assert yaml_collection.yaml_version == version_file.read()


def test_manual_suite(yaml_collection: YamlCollectionDeclaration) -> None:
    expected_manual_test_cases = 2

    assert "FirstManualSuite" in yaml_collection.test_suites.keys()
    manual_suite = yaml_collection.test_suites["FirstManualSuite"]
    assert len(manual_suite.test_cases) == expected_manual_test_cases
    for test_case in manual_suite.test_cases.values():
        assert isinstance(test_case, YamlCaseDeclaration)
        assert test_case.test_type == YamlTestType.MANUAL


def test_automated_suite(yaml_collection: YamlCollectionDeclaration) -> None:
    expected_manual_test_cases = 0
    expected_automated_test_cases = 3
    expected_semi_automated_test_cases = 1
    expected_simulated_test_cases = 0

    # Assert automated and semi-automated tests cases
    assert "FirstChipToolSuite" in yaml_collection.test_suites.keys()
    automated_suite = yaml_collection.test_suites["FirstChipToolSuite"]
    assert (
        len(automated_suite.test_cases)
        == expected_automated_test_cases + expected_semi_automated_test_cases
    )

    type_count = dict.fromkeys(YamlTestType, 0)
    for test_case in automated_suite.test_cases.values():
        assert isinstance(test_case, YamlCaseDeclaration)
        type_count[test_case.test_type] += 1

    assert type_count[YamlTestType.AUTOMATED] == expected_automated_test_cases
    assert type_count[YamlTestType.SEMI_AUTOMATED] == expected_semi_automated_test_cases
    assert type_count[YamlTestType.SIMULATED] == expected_simulated_test_cases
    assert type_count[YamlTestType.MANUAL] == expected_manual_test_cases


def test_simulated_suite(yaml_collection: YamlCollectionDeclaration) -> None:
    expected_simulated_test_cases = 1

    assert "FirstAppSuite" in yaml_collection.test_suites.keys()
    simulated_suite = yaml_collection.test_suites["FirstAppSuite"]
    assert len(simulated_suite.test_cases) == expected_simulated_test_cases
    for test_case in simulated_suite.test_cases.values():
        assert isinstance(test_case, YamlCaseDeclaration)
        assert test_case.test_type == YamlTestType.SIMULATED
