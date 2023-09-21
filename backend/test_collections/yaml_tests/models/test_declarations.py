from typing import Type

from app.test_engine.models.test_declarations import (
    TestCaseDeclaration,
    TestCollectionDeclaration,
    TestSuiteDeclaration,
)

from .test_case import YamlTestCase
from .test_suite import SuiteType, YamlTestSuite
from .yaml_test_folder import YamlTestFolder
from .yaml_test_models import YamlTest, YamlTestType


class YamlCollectionDeclaration(TestCollectionDeclaration):
    def __init__(self, folder: YamlTestFolder, name: str) -> None:
        super().__init__(path=str(folder.path), name=name)
        self.yaml_version = folder.version


class YamlSuiteDeclaration(TestSuiteDeclaration):
    """Direct initialization for YAML Test Suite."""

    class_ref: Type[YamlTestSuite]

    def __init__(self, name: str, suite_type: SuiteType, version: str) -> None:
        super().__init__(
            YamlTestSuite.class_factory(
                name=name,
                suite_type=suite_type,
                yaml_version=version,
            )
        )


class YamlCaseDeclaration(TestCaseDeclaration):
    """Direct initialization for YAML Test Case."""

    class_ref: Type[YamlTestCase]

    def __init__(self, test: YamlTest, yaml_version: str) -> None:
        super().__init__(
            YamlTestCase.class_factory(test=test, yaml_version=yaml_version)
        )

    @property
    def test_type(self) -> YamlTestType:
        return self.class_ref.yaml_test.type
