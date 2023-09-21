from app.crud.base import CRUDBaseRead
from app.models.test_suite_metadata import TestSuiteMetadata


class CRUDTestSuiteMetadata(CRUDBaseRead[TestSuiteMetadata]):
    pass


test_suite_metadata = CRUDTestSuiteMetadata(TestSuiteMetadata)
