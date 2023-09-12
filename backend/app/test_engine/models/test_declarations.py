import re
from typing import Dict, Type

from app.test_engine.models.test_metadata import TestMetadata

from . import TestCase, TestSuite


class TestCaseDeclaration(object):
    def __init__(self, class_ref: Type[TestCase]) -> None:
        self.class_ref = class_ref

    def as_dict(self) -> dict:
        return {"metadata": self.metadata}

    @property
    def pics(self) -> set[str]:
        return self.class_ref.pics()

    @property
    def metadata(self) -> TestMetadata:
        return self.class_ref.metadata

    @property
    def public_id(self) -> str:
        return self.class_ref.public_id()


class TestSuiteDeclaration(object):
    def __init__(self, class_ref: Type[TestSuite]) -> None:
        self.class_ref = class_ref
        self.test_cases: Dict[str, TestCaseDeclaration] = {}

    @property
    def public_id(self) -> str:
        return self.class_ref.public_id()

    def add_test_case(self, test: TestCaseDeclaration) -> None:
        self.test_cases[test.public_id] = test

    def sort_test_cases(self) -> None:
        """This will sort test cases by their public_id.

        The sorting is done using natural sorting (ignoring case) using this algorithm:
            1. `natural_sort_key` method will split the test case public id
                into non-numeric and numeric chunks.

                1.a The split is done using regEx `re.split("(d+)", s[0])`
                1.b numeric chunks are converted to int
                1.c non-numeric chunks are lowercased.

                Examples:
                "TC-CADMIN-1.10" -> ['tc-cadmin-', 1, '.', 10, '']
                "TC-CADMIN-1.11" -> ['tc-cadmin-', 1, '.', 11, '']
                "TC-CADMIN-1.9" -> ['tc-cadmin-', 1, '.', 9, '']


            2. Python's `sorted` will sort the test_cases by `natural_sort_key`.
                This is done chunk by chunk.

                From the example above the first 3 chunks are the same, but the chunks
                at index 3, are numbers that differ and result in this sorting:

                    1. TC-CADMIN-1.9
                    2. TC-CADMIN-1.10
                    3. TC-CADMIN-1.11
        """

        def natural_sort_key(pair: tuple[str, TestCaseDeclaration]) -> list:
            public_id = pair[0]
            chunks = re.split(r"(\d+)", public_id)
            return [int(c) if c.isdigit() else c.lower() for c in chunks]

        self.test_cases = dict(sorted(self.test_cases.items(), key=natural_sort_key))

    def as_dict(self) -> dict:
        return {
            "metadata": self.metadata,
            "test_cases": {k: v.as_dict() for k, v in self.test_cases.items()},
        }

    @property
    def metadata(self) -> TestMetadata:
        return self.class_ref.metadata


class TestCollectionDeclaration(object):
    def __init__(self, path: str, name: str) -> None:
        self.name = name
        self.path = path
        self.test_suites: Dict[str, TestSuiteDeclaration] = {}

    def add_test_suite(self, suite: TestSuiteDeclaration) -> None:
        self.test_suites[suite.public_id] = suite

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "test_suites": {k: v.as_dict() for k, v in self.test_suites.items()},
        }
