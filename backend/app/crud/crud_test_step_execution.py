from app.crud.base import CRUDBaseRead
from app.models.test_step_execution import TestStepExecution


class CRUDTestStepExecution(CRUDBaseRead[TestStepExecution]):
    pass


test_step_execution = CRUDTestStepExecution(TestStepExecution)
