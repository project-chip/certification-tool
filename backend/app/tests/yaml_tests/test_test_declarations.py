from unittest import mock

from test_collections.yaml_tests.models.test_declarations import (
    YamlCaseDeclaration,
    YamlSuiteDeclaration,
)
from test_collections.yaml_tests.models.test_suite import SuiteType
from test_collections.yaml_tests.models.yaml_test_models import YamlTest


def test_yaml_suite_declaration() -> None:
    name = "TestName"
    type = SuiteType.AUTOMATED
    version = "SomeVersionStr"

    with mock.patch(
        "test_collections.yaml_tests.models.test_suite.YamlTestSuite.class_factory"
    ) as class_factory, mock.patch(
        "app.test_engine.models.test_declarations.TestSuiteDeclaration.__init__"
    ) as declaration_init:
        YamlSuiteDeclaration(name=name, suite_type=type, version=version)
        class_factory.assert_called_once_with(
            name=name, suite_type=type, yaml_version=version
        )
        declaration_init.assert_called_once()


def test_yaml_case_declaration() -> None:
    test = YamlTest(name="TestTest", config={}, tests=[])
    version = "SomeVersionStr"
    with mock.patch(
        "test_collections.yaml_tests.models.test_case.YamlTestCase.class_factory"
    ) as class_factory, mock.patch(
        "app.test_engine.models.test_declarations.TestCaseDeclaration.__init__"
    ) as declaration_init:
        YamlCaseDeclaration(test=test, yaml_version=version)
        class_factory.assert_called_once_with(test=test, yaml_version=version)
        declaration_init.assert_called_once()
