from app.crud.base import CRUDBaseRead
from app.models.test_case_metadata import TestCaseMetadata


class CRUDTestCaseMetadata(CRUDBaseRead[TestCaseMetadata]):
    pass


test_case_metadata = CRUDTestCaseMetadata(TestCaseMetadata)
