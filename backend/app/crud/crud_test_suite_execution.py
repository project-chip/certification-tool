from app.crud.base import CRUDBaseRead
from app.models.test_suite_execution import TestSuiteExecution


class CRUDTestSuiteExecution(CRUDBaseRead[TestSuiteExecution]):
    pass


test_suite_execution = CRUDTestSuiteExecution(TestSuiteExecution)
