from app.crud.base import CRUDBaseRead
from app.models.test_case_execution import TestCaseExecution


class CRUDTestCaseExecution(CRUDBaseRead[TestCaseExecution]):
    pass


test_case_execution = CRUDTestCaseExecution(TestCaseExecution)
