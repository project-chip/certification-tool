from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase, CRUDOperationNotSupported
from app.models.test_run_config import TestRunConfig
from app.schemas.test_run_config import TestRunConfigCreate, TestRunConfigUpdate
from app.test_engine.test_script_manager import test_script_manager


class CRUDTestRunConfig(
    CRUDBase[TestRunConfig, TestRunConfigCreate, TestRunConfigUpdate]
):
    # We overrite the create method, to add validation of valid selected tests
    def create(self, db: Session, *, obj_in: TestRunConfigCreate) -> TestRunConfig:
        test_script_manager.validate_test_selection(obj_in.selected_tests)
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = TestRunConfig(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> TestRunConfig:
        raise CRUDOperationNotSupported("You cannot remove Test Run Config")


test_run_config = CRUDTestRunConfig(TestRunConfig)
