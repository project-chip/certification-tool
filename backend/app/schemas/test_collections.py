from typing import Dict

from pydantic import BaseModel


class TestMetadata(BaseModel):
    public_id: str
    version: str
    title: str
    description: str


class TestCase(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    metadata: TestMetadata


class TestSuite(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    metadata: TestMetadata
    test_cases: Dict[str, TestCase]


class TestCollection(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    name: str
    path: str
    test_suites: Dict[str, TestSuite]


class TestCollections(BaseModel):
    test_collections: Dict[str, TestCollection]
